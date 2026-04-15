from collections import defaultdict
import pandas as pd
import json
import webbrowser
import os
import jinja2
import numpy as np

class ActionFinder:
    def __init__(self, indicator_filename=None, qtable_filename=None):
        self.indicator_filename = indicator_filename
        self.folder_name = os.path.basename(os.path.dirname(indicator_filename))
        self.indicator_data = pd.read_csv(indicator_filename).rename(
                {
                    'Economic Impact'.upper(): 'EI',
                    'Life Assessment'.upper(): 'LA',
                    'Maintenance Stratgy'.upper(): 'MS',
                    'Economic Impact': 'EI',
                    'Life Assessment': 'LA',
                    'Maintenance Strategy': 'MS'
                }, axis=1)

        self.indicator_categorical = None # Indicators with categorical values
        self.indicator_results = None # Results with actions
        self.indicator_w_flexibility = None # Results after applying flexibility
        self.qtable_filename = qtable_filename
        self.qtable = pd.read_excel(qtable_filename, sheet_name='Q_table final')
        self.customDataActions = None
        self.foundAction = ""
        self.html_filename = None

        self.results_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Result', 'future_actions', self.folder_name)
        os.makedirs(self.results_folder, exist_ok=True)

    def calculateHML(self):
        """Map indicator values from numerical to categorical"""
        self.indicator_categorical = self.indicator_data.copy()
        columns = self.indicator_categorical.columns[1:-1]
        def func(value):
            if 1.0 >= value >= 0.75:
                return 'H'
            elif 0.75 > value >= 0.50:
                return 'M'
            elif 0.50 > value >= 0.00:
                return 'L'
            else:
                raise ValueError("Data contains values out of range [1.0, 0.0]")
        try:
            self.indicator_categorical.loc[:, columns] = self.indicator_categorical.loc[:, columns].applymap(func)
        except ValueError as e:
            print("DEBUG:")
            print(f"  columns: {columns}")
            print("DATA with ERRORS == True:")
            print(self.indicator_categorical.loc[:, columns] < 0.0 | self.indicator_categorical.loc[:, columns] > 1.0)

    def calculateAllPossibleAction(self):
        data_dict = {}
        columns = self.indicator_categorical.columns[1:-1]

        data = self.qtable.iloc[3:, 1:].to_numpy()
        df_columns = self.qtable.iloc[2, 1:4].to_list() + self.qtable.iloc[1, 4:].to_list()
        df = pd.DataFrame(data=data, columns=df_columns)
        df = df.convert_dtypes()
        df = df.groupby(columns.to_list()).mean(numeric_only=True)

        def tupleorvalue(x):
            v = tuple(x)
            if len(v) == 1:
                v = v[0]
            return v
        values = list(map(tupleorvalue, self.indicator_categorical.loc[:, columns].to_numpy()))
        print('df')
        print(df)
        print('df-info')
        print(df.info())
        print('values')
        print(values)
        self.decisions = df.loc[values].idxmax(axis=1)
        self.decisions.name = 'Action'
        self.decisions = self.decisions.reset_index()
    
    def compute_flexibility(self):
        index_col = self.indicator_data.columns[0]
        state_cols = self.indicator_categorical.columns[1:-1].to_list()
        N = len(state_cols)

        V = self.indicator_data.loc[:, state_cols].to_numpy()[:, None, ...]
        A = self.indicator_data.loc[:, 'action']

        T = pd.read_csv('../files/weights.csv').set_index('action')

        t = T.loc[A, state_cols].to_numpy()[:, None, ...]

        res = V @ (np.eye(N) * t)
        res = res[:, 0, ...]

        df = pd.DataFrame(data=res, columns=state_cols)
        df[index_col] = self.indicator_data[index_col]
        df['action'] = A
        df = df.loc[:, [index_col] + state_cols + ['action']]

        self.indicator_w_flexibility = df

    def findingAction(self):        
        # columns = self.indicator_categorical.columns[1:-1].to_list()
        # decisions = self.decisions.set_index(columns)
        # actions = [decisions.loc[ind].to_array()[0] for ind in self.indicator_categorical[columns].itertuples(index=False)]
        actions = self.decisions['Action']

        self.indicator_results = self.indicator_categorical.copy().loc[:, self.indicator_categorical.columns[:-1]]
        self.indicator_results.columns = list(map(str.upper, self.indicator_results.columns))

        self.indicator_results['ACTION'] = actions
        self.indicator_data['action'] = actions

    def actions_to_csv(self):
        barename = os.path.basename(os.path.splitext(self.indicator_filename)[0])
        results_filename = os.path.join(self.results_folder, barename)
        actions_filename = results_filename + '_actions.csv'
        self.indicator_results.to_csv(actions_filename, index=False)

    def actions_to_html(self):
        barename = os.path.basename(os.path.splitext(self.indicator_filename)[0])
        results_filename = os.path.join(self.results_folder, barename)
        self.html_filename = results_filename + '.html'
        html_page = render_data(self.indicator_results)
        with open(self.html_filename, "w") as f:
            f.write(html_page)

    def flexibility_to_csv(self):
        barename = os.path.basename(os.path.splitext(self.indicator_filename)[0])
        results_filename = os.path.join(self.results_folder, barename)
        self.indicator_w_flexibility_filename = results_filename + '_with_flexibility.csv'
        self.indicator_w_flexibility.to_csv(self.indicator_w_flexibility_filename)

    def simulate_next_state(self, state, actions, transitions):
        pass

    def show(self):
        if self.html_filename is None:
            print("HTML was not loaded")
        else:
            webbrowser.open(self.html_filename)

def render_data(data):
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader("../res/templates"),
        #autoescape=jinja2.select_autoescape(),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template("template.html")
    html_page = template.render(data=data, root_folder=os.path.dirname(os.path.dirname(__file__)))
    return html_page
