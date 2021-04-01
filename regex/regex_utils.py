import re


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
                              "undermatches": list()} for exp in dict_regexps.keys()}

    def regex(self, text, label, exp, lower=True):
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
            self.evaluate(True, exp, label, text)
        else:
            self.evaluate(False, exp, label, text)

    def evaluate(self, is_matched, exp, label, text):

        # True positive
        if exp == label and is_matched is True:
            self.results[exp]["matched"] += 1
        # False positive
        elif exp == label and is_matched is True:
            print("False positive.")
            self.results[exp]["overmatched"] += 1
            self.results[exp]["overmatches"].append(text)
        # False negative
        elif exp == label and is_matched is False:
            print("False negative.")
            self.results[exp]["unmatched"] += 1
            self.results[exp]["undermatches"].append(text)
        # True negative
        else:
            pass

