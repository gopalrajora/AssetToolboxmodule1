from collections import defaultdict
import pandas as pd
import json
import webbrowser
import os
import jinja2
import numpy as np

class ActionFinder:
    def __init__(self, indicator_filename=None, qtable_filename=None):
        print(indicator_filename)
        self.folder_name = os.path.basename(os.path.dirname(indicator_filename))
        self.indicator_filename = indicator_filename
        self.indicator_data = pd.read_csv(indicator_filename).rename(
                    {'Economic Impact'.upper(): 'EI',
                    'Life Assessment'.upper(): 'LA',
                    'Maintenance Stratgy'.upper(): 'MS'},
                   axis=1)
        self.indicator_categorical = None # Indicators with categorical values
        self.indicator_results = None # Results with actions
        self.indicator_w_flexibility = None # Results after applying flexibility
        self.qtable_filename = qtable_filename
        self.qtable = pd.read_excel(qtable_filename, sheet_name='Q_table final')
        self.customDataActions = None
        self.foundAction = ""
        self.html_filenames = []

        self.results_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Result',
                                                   'future_actions', self.folder_name)

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

        data2 = self.qtable.to_dict()

        if data2.get('Q_TABLE'):
            data2.pop('Q_TABLE')

        for i, x in enumerate(data2):
            if i < len(columns):
                for i2, y in enumerate(data2[x]):
                    if i2 == 2:
                        data_dict[data2[x][y]] = list(data2[x].values())[3:]
            else:
                for i2, y in enumerate(data2[x]):
                    if i2 == 1:
                        data_dict[data2[x][y]] = list(data2[x].values())[3:]

        df1 = pd.DataFrame(data_dict)
        # df1.drop(float('nan'), axis=1, inplace=True)
        json_rev_data = json.loads(df1.to_json(orient='records'))

        action = []

        for dictionary in json_rev_data:
            name_list = []
            value_list = []

            for key in dictionary:
                if key not in self.indicator_categorical.columns[1:-1]:
                    name_list.append(key)
                    value_list.append(dictionary[key])

            max_value = max(value_list)

            action.append(name_list[value_list.index(max_value)])

        fields_to_pop = [
                        'Decrease its use rate. (More energy, more operations.)',
                        'Increase its use rate. (More energy, more operations.)',
                        'Inspect current external aspect',
                        'Keep the current maintenance',
                        'Lengthen the maintenance cycle',
                        'Replacement',
                        'Shorten the maintenance cycle']

        for i, dictionary in enumerate(json_rev_data):
            dictionary['action'] = action[i]
            for fields in fields_to_pop:
                dictionary.pop(fields)

        self.decisions = pd.DataFrame(json_rev_data)
    
    def compute_flexibility(self):
        index_col = self.indicator_data.columns[0]
        state_cols = ['EI', 'LA', 'MS']
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
        columns = self.indicator_categorical.columns[1:-1].to_list()
        decisions = self.decisions.set_index(columns)
        actions = [decisions.loc[ind].array[0] for ind in self.indicator_categorical[columns].itertuples(index=False)]

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
        self.html_filenames.append(self.html_filename)

    def flexibility_to_csv(self):
        barename = os.path.basename(os.path.splitext(self.indicator_filename)[0])
        results_filename = os.path.join(self.results_folder, barename)
        self.indicator_w_flexibility_filename = results_filename + '_with_flexibility.csv'
        self.indicator_w_flexibility.to_csv(self.indicator_w_flexibility_filename)

    def simulate_next_state(self, state, actions, transitions):
        pass

    def show(self):
        for html_filename in self.html_filenames:
            webbrowser.open(html_filename)

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
