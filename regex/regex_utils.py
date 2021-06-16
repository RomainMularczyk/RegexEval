import os
import re
import numpy as np
import pandas as pd
from sklearn.metrics import ConfusionMatrixDisplay


class RegexEval:
    """Defines a series of helpers to build and evaluate regular expressions.
    Inputs :
    - dict_regexps : dictionary that matches the pattern to find and its associated regular expression [dict].
     Expected shape : {expression: regex,
                       expression: regex,
                       ...}
    - dict_results : dictionary that keep tracks of metrics to evaluate the regular expression tested [dict].
     Expected shape : {matched: int(),
                       unmatched: int(),
                       overmatched: int(),
                       overmatches: list(),
                       undermatches: list()}
    """

    def __init__(self, dict_regexps):
        self.regexps = {exp: regex for exp, regex in dict_regexps.items()}
        self.results = {exp: {"matched": int(),
                              "unmatched": int(),
                              "overmatched": int(),
                              "overmatches": list(),
                              "overmatches_focus": list(),
                              "overmatches_id": list(),
                              "undermatches": list(),
                              "undermatches_focus": list(),
                              "undermatches_id": list(),
                              "nomatched": int()} for exp in dict_regexps.keys()}

    def regex(self, doc_id, text, label, exp, lower=True):
        """Defines a regex and searches for matching patterns.
        Inputs :
        - text : input text [string]
        - reg : regular expression ["r" string]
        - lower : defines if text should be passed to lower [bool]
        """

        regex = self.regexps[exp]

        if lower:
            text = text.lower()
            
        # Add a regex result property
        self.regex_res = re.search(regex, text)

        if self.regex_res:
            self.evaluate(True, doc_id, text, label, exp)
        else:
            self.evaluate(False, doc_id, text, label, exp)

    def evaluate(self, is_matched, doc_id, text, label, exp):
        """Evaluates a regex and stores different informations.
        - Matched : How many regex lead to True Positives
        - Overmatched : How many regex lead to False Positives
        - Undermatched : How many regex lead to False Negatives
        - Nomatched : How many regex lead to True Negatives
        """

        # True positive
        if exp == label and is_matched is True:
            self.results[exp]["matched"] += 1
        # False positive
        elif exp != label and is_matched is True:
            self.results[exp]["overmatched"] += 1
            self.results[exp]["overmatches"].append(text)
            try:
                self.results[exp]["overmatches_focus"].append(text[self.regex_res.span()[0] - 10:self.regex_res.span()[1]])
            except:
                self.results[exp]["overmatches_focus"].append(0)
            self.results[exp]["overmatches_id"].append(doc_id)
        # False negative
        elif exp == label and is_matched is False:
            self.results[exp]["unmatched"] += 1
            self.results[exp]["undermatches"].append(text)
            # 
            try:
                self.results[exp]["undermatches_focus"].append(text[self.regex_res.span()[0] - 10:self.regex_res.span()[1]])
            except:
                self.results[exp]["undermatches_focus"].append(0)
            self.results[exp]["undermatches_id"].append(doc_id)
        # True negative
        else:
            self.results[exp]["nomatched"] += 1

    def export_results(self):
        """Exports the regex evaluation results in CSV tables.
        Each regex gets its own couple of overmatches (False Positives)
        and undermatches (False Negatives) table.
        """

        os.makedirs("../data/export", exist_ok=True)

        for exp, values in self.results.items():
            df_overmatch = pd.DataFrame({"overmatches_id": values["overmatches_id"],
                               "overmatches": values["overmatches"],
                               "overmatches_focus": values["overmatches_focus"]})

            df_overmatch.to_csv(os.path.join("../data/export", "overmatch_" + exp + ".csv"), sep=";", encoding="utf-8")

            df_undermatch = pd.DataFrame({"undermatches_id": values["undermatches_id"],
                                          "undermatches": values["undermatches"],
                                          "undermatches_focus": values["undermatches_focus"]})

            df_undermatch.to_csv(os.path.join("../data/export", "undermatch_" + exp + ".csv"), sep=";", encoding="utf-8")

    def plot_confusion_matrix(self, exp):
        """Plots a confusion matrix that synthesizes the regex matching
        patterns results.
        """
        
        data = np.array([[self.results[exp]["matched"], self.results[exp]["unmatched"]],
                         [self.results[exp]["overmatched"], self.results[exp]["nomatched"]]])
        
        ConfusionMatrixDisplay(data).plot()