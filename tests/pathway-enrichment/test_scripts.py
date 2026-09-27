"""Tests for the pathway-enrichment input handling.

The enrichment call itself goes to Enrichr or a local GMT, so what is worth
testing offline is everything that decides *which genes, in which order* get
sent -- and that is where enrichment analyses usually go wrong. A mouse symbol
left upper-cased silently matches nothing in a mouse library; a ranking built
from an unsigned p-value puts up- and down-regulated genes at the same end of
the list and quietly inverts GSEA's answer.
"""

from __future__ import annotations

import argparse
import contextlib
import importlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import pytest

import skill_contract

SKILL_ROOT = Path(__file__).resolve().parents[2] / "skills" / "pathway-enrichment"
SCRIPTS = SKILL_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

pd = pytest.importorskip("pandas", reason="pathway-enrichment needs pandas")
pytest.importorskip("numpy", reason="pathway-enrichment needs numpy")
pytest.importorskip("gseapy", reason="run_enrichment imports gseapy at module scope")

import run_enrichment  # noqa: E402

CliHelpTests = skill_contract.cli.help_test_case(SKILL_ROOT)


class SymbolCleaningTests(unittest.TestCase):
    def test_human_symbols_are_upper_cased(self) -> None:
        self.assertEqual(
            run_enrichment._clean_symbols(["tp53", "Brca1"], "human"),
            ["TP53", "BRCA1"],
        )

    def test_mouse_symbols_are_title_cased(self) -> None:
        # Mouse libraries key on Trp53, not TRP53 -- getting this wrong returns
        # an empty enrichment with no error.
        self.assertEqual(
            run_enrichment._clean_symbols(["TRP53", "brca1"], "mouse"),
            ["Trp53", "Brca1"],
        )

    def test_an_unknown_organism_leaves_case_alone(self) -> None:
        self.assertEqual(
            run_enrichment._clean_symbols(["dpp", "Hh"], "fly"), ["dpp", "Hh"]
        )

    def test_blank_and_placeholder_entries_are_dropped(self) -> None:
        self.assertEqual(
            run_enrichment._clean_symbols(
                ["TP53", "", "   ", "nan", "NaN", "None", "BRCA1"], "human"
            ),
            ["TP53", "BRCA1"],
        )

    def test_duplicates_are_removed_after_normalisation(self) -> None:
        # "tp53" and "TP53" are the same gene once case is normalised.
        self.assertEqual(
            run_enrichment._clean_symbols(["tp53", "TP53", "Tp53"], "human"), ["TP53"]
        )

    def test_input_order_is_preserved(self) -> None:
        self.assertEqual(
            run_enrichment._clean_symbols(["c", "a", "b", "a"], "other"),
            ["c", "a", "b"],
        )

    def test_surrounding_whitespace_is_stripped(self) -> None:
        self.assertEqual(run_enrichment._clean_symbols([" TP53 "], "human"), ["TP53"])


class GeneListReadingTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self._temporary.cleanup)
        self.root = Path(self._temporary.name)

    def test_a_plain_text_list_is_read_one_gene_per_line(self) -> None:
        path = self.root / "genes.txt"
        path.write_text("TP53\nBRCA1\n\nEGFR\n", encoding="utf-8")
        self.assertEqual(
            run_enrichment._read_gene_list(path), ["TP53", "BRCA1", "EGFR"]
        )

    def test_a_csv_uses_its_first_column(self) -> None:
        path = self.root / "genes.csv"
        path.write_text("gene,log2FC\nTP53,1.2\nBRCA1,-0.8\n", encoding="utf-8")
        self.assertEqual(run_enrichment._read_gene_list(path), ["TP53", "BRCA1"])

    def test_a_tsv_is_split_on_tabs_not_commas(self) -> None:
        path = self.root / "genes.tsv"
        path.write_text("gene\tlog2FC\nTP53\t1.2\nBRCA1\t-0.8\n", encoding="utf-8")
        self.assertEqual(run_enrichment._read_gene_list(path), ["TP53", "BRCA1"])


class RankingTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self._temporary.cleanup)
        self.root = Path(self._temporary.name)

    def _deseq2(self, text: str) -> Path:
        path = self.root / "deseq2.csv"
        path.write_text(text, encoding="utf-8")
        return path

    def test_the_wald_statistic_is_preferred_when_present(self) -> None:
        path = self._deseq2(
            "gene,baseMean,log2FoldChange,stat,pvalue\n"
            "TP53,100,2.0,5.0,1e-6\n"
            "BRCA1,100,-1.0,-3.0,1e-3\n"
            "EGFR,100,0.1,0.2,0.8\n"
        )
        ranks = run_enrichment._build_rank_from_deseq2(path, "human")
        self.assertEqual(list(ranks.index), ["TP53", "EGFR", "BRCA1"])
        self.assertEqual(ranks["TP53"], 5.0)

    def test_the_fallback_metric_keeps_the_direction_of_the_fold_change(self) -> None:
        # sign(log2FC) * -log10(p): a strongly down-regulated gene must land at
        # the bottom of the ranking, not the top.
        path = self._deseq2(
            "gene,log2FoldChange,pvalue\n"
            "UP,3.0,1e-10\n"
            "DOWN,-3.0,1e-10\n"
            "FLAT,0.1,0.9\n"
        )
        ranks = run_enrichment._build_rank_from_deseq2(path, "human")
        self.assertEqual(list(ranks.index), ["UP", "FLAT", "DOWN"])
        self.assertGreater(ranks["UP"], 0)
        self.assertLess(ranks["DOWN"], 0)

    def test_a_zero_pvalue_is_clipped_rather_than_becoming_infinite(self) -> None:
        path = self._deseq2("gene,log2FoldChange,pvalue\nA,2.0,0.0\nB,1.0,0.5\n")
        ranks = run_enrichment._build_rank_from_deseq2(path, "human")
        self.assertTrue(all(abs(value) < float("inf") for value in ranks))
        self.assertEqual(ranks.idxmax(), "A")

    def test_a_table_with_neither_metric_exits_naming_its_columns(self) -> None:
        path = self._deseq2("gene,baseMean,padj\nTP53,100,0.01\n")
        with self.assertRaises(SystemExit) as raised:
            run_enrichment._build_rank_from_deseq2(path, "human")
        self.assertIn("baseMean", str(raised.exception))

    def test_column_names_are_matched_case_insensitively(self) -> None:
        path = self._deseq2("gene,LOG2FOLDCHANGE,PVALUE\nA,2.0,1e-5\nB,-1.0,1e-2\n")
        ranks = run_enrichment._build_rank_from_deseq2(path, "human")
        self.assertEqual(list(ranks.index), ["A", "B"])

    def test_rows_with_missing_statistics_are_dropped(self) -> None:
        path = self._deseq2("gene,stat\nA,3.0\nB,\nC,1.0\n")
        ranks = run_enrichment._build_rank_from_deseq2(path, "human")
        self.assertEqual(list(ranks.index), ["A", "C"])

    def test_duplicate_symbols_keep_their_first_occurrence(self) -> None:
        path = self._deseq2("gene,stat\ntp53,5.0\nTP53,1.0\n")
        ranks = run_enrichment._build_rank_from_deseq2(path, "human")
        self.assertEqual(list(ranks.index), ["TP53"])
        self.assertEqual(ranks["TP53"], 5.0)

    def test_the_ranking_is_returned_in_descending_order(self) -> None:
        path = self._deseq2("gene,stat\nA,1.0\nB,9.0\nC,-4.0\n")
        ranks = run_enrichment._build_rank_from_deseq2(path, "human")
        self.assertEqual(list(ranks.values), sorted(ranks.values, reverse=True))


class RankedFileTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self._temporary.cleanup)
        self.root = Path(self._temporary.name)

    def _rnk(self, text: str) -> Path:
        path = self.root / "ranked.rnk"
        path.write_text(text, encoding="utf-8")
        return path

    def test_a_headerless_two_column_file_is_read_directly(self) -> None:
        ranks = run_enrichment._read_rnk(self._rnk("TP53,5.0\nBRCA1,-2.0\n"), "human")
        self.assertEqual(list(ranks.index), ["TP53", "BRCA1"])
        self.assertEqual(ranks["TP53"], 5.0)

    def test_a_header_row_is_detected_and_dropped(self) -> None:
        ranks = run_enrichment._read_rnk(
            self._rnk("gene,score\nTP53,5.0\nBRCA1,-2.0\n"), "human"
        )
        self.assertEqual(list(ranks.index), ["TP53", "BRCA1"])

    def test_a_single_column_file_is_refused(self) -> None:
        with self.assertRaises(SystemExit) as raised:
            run_enrichment._read_rnk(self._rnk("TP53\nBRCA1\n"), "human")
        self.assertIn("two columns", str(raised.exception))

    def test_symbols_are_normalised_for_the_organism(self) -> None:
        ranks = run_enrichment._read_rnk(self._rnk("trp53,5.0\n"), "mouse")
        self.assertEqual(list(ranks.index), ["Trp53"])

    def test_rows_with_unparseable_scores_are_dropped(self) -> None:
        ranks = run_enrichment._read_rnk(self._rnk("A,1.0\nB,n/a\nC,2.0\n"), "human")
        self.assertEqual(sorted(ranks.index), ["A", "C"])

    def test_the_result_is_sorted_descending(self) -> None:
        ranks = run_enrichment._read_rnk(self._rnk("A,1.0\nB,9.0\nC,-4.0\n"), "human")
        self.assertEqual(list(ranks.index), ["B", "A", "C"])


class LibraryTests(unittest.TestCase):
    def test_the_default_libraries_are_named_and_versioned(self) -> None:
        # Enrichr library names carry a year; an unversioned name silently
        # resolves to whatever is current and makes results irreproducible.
        self.assertTrue(run_enrichment.DEFAULT_LIBRARIES)
        for library in run_enrichment.DEFAULT_LIBRARIES:
            with self.subTest(library=library):
                # The year may be terminal (Reactome_2022) or followed by a
                # species suffix (KEGG_2021_Human).
                self.assertRegex(library, r"_\d{4}(_[A-Za-z]+)?$")

    def test_the_default_set_is_free_of_duplicates(self) -> None:
        self.assertEqual(
            len(set(run_enrichment.DEFAULT_LIBRARIES)),
            len(run_enrichment.DEFAULT_LIBRARIES),
        )


class BackgroundTests(unittest.TestCase):
    """What --background actually reaches, with every Enrichr call mocked out.

    gseapy's docstring says a background is ignored for Enrichr library names,
    but its code (1.3.0, 1.3.1) uploads a gene-list background to Enrichr's
    Speedrichr background API, which only the main human/mouse site offers. The
    script warns only where the flag really cannot take effect.
    """

    def setUp(self) -> None:
        self._temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self._temporary.cleanup)
        self.root = Path(self._temporary.name)
        self.genes = self.root / "hits.txt"
        self.genes.write_text("TP53\nEGFR\nMYC\nKRAS\nBRCA1\n", encoding="utf-8")
        self.universe = self.root / "universe.txt"
        self.universe.write_text(
            "TP53\nEGFR\nMYC\nKRAS\nBRCA1\nGAPDH\nACTB\n", encoding="utf-8"
        )

    def _run_ora(self, libraries, organism="human", background=True):
        args = argparse.Namespace(
            genes=str(self.genes),
            background=str(self.universe) if background is True else background,
            libraries=libraries,
            organism=organism,
            fdr=0.05,
        )
        result = mock.Mock()
        result.results = pd.DataFrame(
            {"Term": ["T1"], "Adjusted P-value": [0.01], "Genes": ["TP53;EGFR"]}
        )
        stderr = io.StringIO()
        with mock.patch.object(
            run_enrichment.gp, "enrichr", return_value=result
        ) as enrichr, contextlib.redirect_stderr(stderr), contextlib.redirect_stdout(
            io.StringIO()
        ):
            run_enrichment.run_ora(args)
        return enrichr, stderr.getvalue()

    def test_non_main_site_organism_warns_that_the_background_is_not_applied(self) -> None:
        enrichr, stderr = self._run_ora(["GO_Biological_Process_2018"], organism="fly")
        self.assertIn("WARNING: --background cannot be applied", stderr)
        self.assertIn("GO_Biological_Process_2018", stderr)
        self.assertIn(".gmt", stderr)  # says how to get the background honoured
        # Behaviour is otherwise unchanged: the background still goes to gseapy.
        self.assertEqual(
            enrichr.call_args.kwargs["background"],
            ["TP53", "EGFR", "MYC", "KRAS", "BRCA1", "GAPDH", "ACTB"],
        )

    def test_the_warning_names_only_the_enrichr_libraries(self) -> None:
        _, stderr = self._run_ora(["WormPathways_2019", "local_sets.gmt"], organism="worm")
        self.assertIn("WormPathways_2019", stderr)
        self.assertNotIn("local_sets.gmt", stderr)

    def test_human_and_mouse_library_names_do_not_warn(self) -> None:
        # The main Enrichr site applies the background through Speedrichr.
        for organism in ("human", "mouse", "Homo sapiens"):
            with self.subTest(organism=organism):
                enrichr, stderr = self._run_ora(["KEGG_2021_Human"], organism=organism)
                self.assertEqual(stderr, "")
                self.assertTrue(enrichr.call_args.kwargs["background"])

    def test_local_gmt_libraries_do_not_warn_for_any_organism(self) -> None:
        _, stderr = self._run_ora(["fly_sets.gmt", "more.GMT"], organism="fly")
        self.assertEqual(stderr, "")

    def test_no_background_means_no_warning(self) -> None:
        enrichr, stderr = self._run_ora(["KEGG_2019"], organism="fly", background=None)
        self.assertEqual(stderr, "")
        self.assertIsNone(enrichr.call_args.kwargs["background"])

    def test_an_empty_background_file_warns_instead_of_being_silently_dropped(self) -> None:
        empty = self.root / "empty.txt"
        empty.write_text("\n  \nnan\n", encoding="utf-8")
        _, stderr = self._run_ora(["KEGG_2021_Human"], background=str(empty))
        self.assertIn("contained no gene symbols", stderr)


class UpstreamBackgroundRoutingTests(unittest.TestCase):
    """Pin the gseapy behaviour the warning logic and docs rely on.

    If a gseapy release stops sending a gene-list background for Enrichr
    library names (or starts honouring it elsewhere), re-check the warning in
    run_enrichment._background_warnings and the skill docs.
    """

    def test_a_gene_list_background_takes_the_speedrichr_path(self) -> None:
        enrichr_module = importlib.import_module("gseapy.enrichr")
        frame = pd.DataFrame({"Gene_set": ["KEGG_2021_Human"], "Term": ["T1"],
                              "Adjusted P-value": [0.01]})
        cls = enrichr_module.Enrichr
        with mock.patch.object(cls, "get_libraries", return_value=["KEGG_2021_Human"]), \
             mock.patch.object(cls, "get_results_with_background",
                               return_value=("x", frame)) as with_bg, \
             mock.patch.object(cls, "get_results", return_value=("x", frame)) as without_bg:
            run_enrichment.gp.enrichr(
                gene_list=["TP53", "EGFR"], gene_sets=["KEGG_2021_Human"],
                organism="human", background=["TP53", "EGFR", "MYC"], outdir=None,
            )
            self.assertTrue(with_bg.called)
            self.assertFalse(without_bg.called)
            self.assertEqual(sorted(with_bg.call_args.args[1]), ["EGFR", "MYC", "TP53"])


if __name__ == "__main__":
    unittest.main()
