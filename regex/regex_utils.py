import os
import re
import numpy as np
import pandas as pd
from typing import Dict
from sklearn.metrics import ConfusionMatrixDisplay


class RegexEval:
    """Defines a series of helpers to build and evaluate regular expressions.
    
    Parameters :
    ------------
    dict_regexps : dict
        Dictionary that matches the pattern to find and its associated regular expression.
        Expected shape : {expression: regex,
                          expression: regex,
                          ...}
    dict_results : dict
        Dictionary that keep tracks of metrics to evaluate the regular expression tested.
    """

    def __init__(self, dict_regexps:Dict) -> None:
        self.regexps = {exp: regex for exp, regex in dict_regexps.items()}
        self.results = {exp: {"matched": int(),
                              "overmatched": int(),
                              "overmatches": list(),
                              "overmatches_focus": list(),
                              "overmatches_actual_label": list(),
                              "overmatches_id": list(),
                              "undermatched": int(),
                              "undermatches": list(),
                              "undermatches_focus": list(),
                              "undermatches_actual_label": list(),
                              "undermatches_id": list(),
                              "nomatched": int()} for exp in dict_regexps.keys()}

    def regex(self, doc_id:int, text:str, label:str, exp:str, lower=True) -> None:
        """Defines a regex and searches for matching patterns.
        
        Parameters :
        ------------
        text : str
            Full text of the document.
        reg : re.Pattern
            Regular expression.
        lower : bool
            Defines if text should be lower cased.
        """

        regex = self.regexps[exp]

        if lower:
            text = text.lower()
            
        # Add a regex result property
        self.regex_res = re.search(regex, text)

        if self.regex_res:
            self.evaluate(is_matched=True,
                          doc_id=doc_id,
                          text=text, 
                          label=label,
                          exp=exp)
        else:
            self.evaluate(is_matched=False,
                          doc_id=doc_id,
                          text=text,
                          label=label,
                          exp=exp)

    def evaluate(self, is_matched:bool, doc_id:int, text:str, label:str, exp:str, window:int=40) -> None:
        """Evaluates a regex and stores different informations.
        - Matched : How many regex lead to True Positives
        - Overmatched : How many regex lead to False Positives
        - Undermatched : How many regex lead to False Negatives
        - Nomatched : How many regex lead to True Negatives
        
        Parameters
        ----------
        is_matched :  bool
            Is True if the regular expression matches a pattern.
        doc_id : int
            Unique ID of the document.
        text : str
            Full text of the document.
        label : str
            Label of the category.
        exp : str
            Key representing the information captured by the associated regular expression.
        window : int
            Value that defines how many caracters ahead and behind the matched pattern should be displayed
            in the results log.
        """

        # True positive
        if exp == label and is_matched is True:
            self.results[exp]["matched"] += 1
        # False positive
        elif exp != label and is_matched is True:
            self.results[exp]["overmatched"] += 1
            self.results[exp]["overmatches"].append(text)
            self.results[exp]["overmatches_actual_label"].append(label)
            try:
                self.results[exp]["overmatches_focus"].append(text[self.regex_res.span()[0] - window:self.regex_res.span()[1] + window])
            except:
                self.results[exp]["overmatches_focus"].append(0)
            self.results[exp]["overmatches_id"].append(doc_id)
        # False negative
        elif exp == label and is_matched is False:
            self.results[exp]["undermatched"] += 1
            self.results[exp]["undermatches"].append(text)
            self.results[exp]["undermatches_actual_label"].append(label)
            try:
                self.results[exp]["undermatches_focus"].append(text[self.regex_res.span()[0] - window:self.regex_res.span()[1] + window])
            except:
                self.results[exp]["undermatches_focus"].append(0)
            self.results[exp]["undermatches_id"].append(doc_id)
        # True negative
        else:
            self.results[exp]["nomatched"] += 1
        

        
    def export_results(self) -> None:
        """Exports the regex evaluation results in CSV tables.
        Each regex gets its own couple of overmatches (False Positives)
        and undermatches (False Negatives) table.
        """

        os.makedirs("../data/export", exist_ok=True)

        for exp, values in self.results.items():
            df_overmatch = pd.DataFrame({"overmatches_id": values["overmatches_id"],
                               "overmatches": values["overmatches"],
                               "overmatches_focus": values["overmatches_focus"],
                               "overmatches_actual_label": values["overmatches_actual_label"]})

            df_overmatch.to_csv(os.path.join("../data/export", "overmatch_" + exp + ".csv"), sep=";", encoding="utf-8")

            df_undermatch = pd.DataFrame({"undermatches_id": values["undermatches_id"],
                                          "undermatches": values["undermatches"],
                                          "undermatches_focus": values["undermatches_focus"],
                                          "undermatches_actual_label": values["undermatches_actual_label"]})

            df_undermatch.to_csv(os.path.join("../data/export", "undermatch_" + exp + ".csv"), sep=";", encoding="utf-8")

            
    def plot_confusion_matrix(self, exp:str) -> None:
        """Plots a confusion matrix that synthesizes the regex matching
        patterns results.
        
        Parameters :
        ------------
        exp : str
            Key representing the information captured by the associated regular expression.
        """
        
        data = np.array([[self.results[exp]["matched"], self.results[exp]["undermatched"]],
                         [self.results[exp]["overmatched"], self.results[exp]["nomatched"]]])
        
        ConfusionMatrixDisplay(data).plot()
    
    def calculate_metrics(self, exp:str, percentage:bool=True) -> Dict:
        """Returns metrics to evaluate the sensibility and specificity of a regex.
        
        Parameters :
        ------------
        exp : str
            Key representing the information captured by the associated regular expression.
            
        Returns :
        ---------
        total : int
            The total number of documents that should be matched.
        dict
            A dictionary containing metrics concerning sensibility and specificity.
        """
        
        total = self.results[exp]["matched"] + self.results[exp]["undermatched"]
        
        if percentage == True:
            return total, {"TP": self.results[exp]["matched"] / total * 100,
                           "FN": self.results[exp]["undermatched"] / total * 100}
        else:
            return total, {"TP": self.results[exp]["matched"],
                           "FP": self.results[exp]["overmatched"],
                           "TN": self.results[exp]["nomatched"],
                           "FN": self.results[exp]["undermatched"]}