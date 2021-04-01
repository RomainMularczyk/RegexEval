import re
import pandas as pd
import os


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
                              "overmatches_id": list(),
                              "undermatches": list(),
                              "undermatches_id": list()} for exp in dict_regexps.keys()}

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

        if re.search(regex, text):
            self.evaluate(True, doc_id, text, label, exp)
        else:
            self.evaluate(False, doc_id, text, label, exp)

    def evaluate(self, is_matched, doc_id, text, label, exp):

        # True positive
        if exp == label and is_matched is True:
            self.results[exp]["matched"] += 1
        # False positive
        elif exp != label and is_matched is True:
            self.results[exp]["overmatched"] += 1
            self.results[exp]["overmatches"].append(text)
            self.results[exp]["overmatches_id"].append(doc_id)
        # False negative
        elif exp == label and is_matched is False:
            self.results[exp]["unmatched"] += 1
            self.results[exp]["undermatches"].append(text)
            self.results[exp]["undermatches_id"].append(doc_id)
        # True negative
        else:
            pass

    def export_results(self):

        os.makedirs("../data/export", exist_ok=True)


        for exp, values in self.results.items():
            df_overmatch = pd.DataFrame({"overmatches_id": values["overmatches_id"],
                               "overmatches": values["overmatches"]})

            df_overmatch.to_csv(os.path.join("../data/export", "overmatch_" + exp + ".csv"), sep=";", encoding="utf-8")

            df_undermatch = pd.DataFrame({"undermatches_id": values["undermatches_id"],
                                          "undermatches": values["undermatches"]})
            
            df_undermatch.to_csv(os.path.join("../data/export", "undermatch_" + exp + ".csv"), sep=";", encoding="utf-8")

