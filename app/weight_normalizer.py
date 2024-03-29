import pandas as pd
import nltk


class WeightsNormalizer:
    """
    Creates objects that compute the Normalized Relation Weight (NRW) for a given burst matrix.

    ### PARAMETERS ###
    ------------------
    To be passed to the constructor:
        1) burst_results (pd.DataFrame)
        2) burst_pairs (pd.DataFrame)
        3) burst_weight_matrix (pd.DataFrame)

    Generated by the class methods:

    ### METHODS ###
    ---------------
    Public:
        1) normalize

    Private helpers:
        2) _total_length
        3) _word_frequency

    See the methods documentation for details.

    ### EXAMPLE ###
    ---------------
    weight_norm = WeightsNormalizer(burst_results=filtered_bursts,
                                    burst_weight)
    weight_norm.normalize(formula='original')
    normalized_weights = weight_norm.burst_norm.dataframe
    normalized_weights = normalized_weights.round(decimals=3)
    """

    def __init__(self, bursts: pd.DataFrame, burst_pairs: pd.DataFrame, burst_weight_matrix: pd.DataFrame):
        """
        :param bursts: a pandas dataframe containing a burst for each row
        :param burst_pairs: a pandas dataframe containing for each row a pair of related bursts
        :param burst_weight_matrix: a pd.DataFrame constructed from the weight-matrix
                                    generated from BurstAssigner.
        """

        self._bursts = bursts.copy()
        self._burst_pairs = burst_pairs.copy()
        self._burst_weight_matrix = burst_weight_matrix.copy()

        # prepare a dataset with size: num_concepts x num_concepts
        self._burst_norm = pd.DataFrame(0.0,
                                        index=self._bursts['keyword'].unique(),
                                        columns=self._bursts['keyword'].unique())

        # TODO SE2020: potenzialmente da eliminare in PRET sempre per le stesse ragioni (serve per trovare le frequenze nel testo se non vengono forniti in input dati relativi all'analisi linguistica come quelli contenuti nel conll)
        self._text_filename = ""

    def normalize(self, formula='original', occ_index_file: str=None):

        """
        - for each word X:
            - for each burst of word X:
                - for each word Y:
                    - for each burst of word Y:
                        - if the two current bursts (B_Xi and B_Yj) are related:
                             - retrieve the weight currently assigned to the relation between these two bursts
                                (i.e.: weights[B_Xi, B_Yj])
                             - find the total length of the bursts of these two words
                             - find the frequency of word X in burst B_Xi and the freq of word Y in burst B_Yj
                                (this implies one additional loop for searching in the text)
                             - compute total number of bursts for word X and Y (non present in the original paper)
                             - compute the current NRW between B_Xi and B_Yj
                             - update the final matrix
                                (i.e. sum curr_NRW to the weight previously stored for relation between word X and Y)

        :param formula (str). Type of normalizing formula. Possible values: 'original', 'modified', 'marzo2019_1', 'marzo2019_2'.
                            TODO: add description of the possible choices
        :param occ_index_file df with the following columns:

                            "Lemma"    "idFrase"    "idParolaStart"

                            If no value is passed, frequencies will be computed using NLTK
                            text processing tools.
        :return: None
        """

        if formula not in ['original', 'modified', 'marzo2019_1', 'marzo2019_2']:
            raise ValueError("Error: the argument 'formula' must be either 'original' or 'modified'.")

        # reset dataframe to zeros if any value has been modified during a first call of the function
        if self._burst_norm.ne(0.0).any().any():
            for col in self._burst_norm.columns:
                self._burst_norm[col] = 0.0

        # precompute the word frequencies in their bursts
        for burst_id in self._bursts.index:
            start = self._bursts.at[burst_id, 'start']
            end = self._bursts.at[burst_id, 'end']
            freq = self._word_frequency(self._bursts.at[burst_id, 'keyword'], start, end,
                                        occ_index_file)
            # add the freq in a column of the same dataframe
            self._bursts.at[burst_id, 'word freq'] = freq

        # precompute the total length of bursts of each word
        tot_burst_len = {}
        for word in self._bursts['keyword'].unique():
            tot_burst_len[word] = self._total_length(word)

        # main body of the method: compare bursts and assign a normalized weight

        # for each word X
        for word_X in self._bursts['keyword'].unique():

            # retrieve the list of indexes in the bursts df assigned to the bursts of word X
            bursts_X_indexes = self._bursts.where(self._bursts['keyword'] == word_X).dropna().index.tolist()

            # for each burst of word X
            for burst_X_i in bursts_X_indexes:
                # don't consider the current burst if the entire row is zero
                if (self._burst_weight_matrix.loc[burst_X_i] == 0).all():
                    pass

                other_words = self._bursts['keyword'].unique().tolist()
                other_words.remove(word_X)

                # for each word different from word X
                for word_Y in other_words:
                    # retrieve the list of indexes in the df assigned to the bursts of word Y
                    bursts_Y_indexes = self._bursts.where(self._bursts['keyword'] == word_Y).dropna().index.tolist()

                    # for each burst of this second word Y
                    for burst_Y_j in bursts_Y_indexes:
                        # don't consider the current burst if the entire column is zero
                        if (self._burst_weight_matrix[burst_Y_j] == 0).all():
                            pass

                        # if the two bursts are related:
                        if self._burst_weight_matrix.at[burst_X_i, burst_Y_j] > 0:
                            # retrieve the weight and freqs
                            relation_weight_BX = self._burst_weight_matrix.at[burst_X_i, burst_Y_j]
                            freq_BX = self._bursts.at[burst_X_i, 'word freq']
                            freq_BY = self._bursts.at[burst_Y_j, 'word freq']

                            # compute NRW using the chosen formula
                            if formula == 'original':
                                NRW = (relation_weight_BX * (freq_BX / tot_burst_len[word_X]) *
                                       (freq_BY / tot_burst_len[word_Y]))
                                """
                                # per dare più peso a i pesi rispetto a lunghezze e frequenze
                                NRW = relation_weight_BX * ( (freq_BX / tot_burst_len[word_X]) +
                                       (freq_BY / tot_burst_len[word_Y])) 
                                       
                                # per esaltare le parole meno frequenti
                                NRW = relation_weight_BX * ( (tot_burst_len[word_X] / freq_BX) +
                                       (tot_burst_len[word_Y] / freq_BY)) 
                                """
                            elif formula == 'modified':
                                # find total number of bursts of these words
                                # TODO: (OPTIM) move it outside the loop
                                num_bursts_X = self._bursts.where(self._bursts['keyword'] == word_X).dropna().shape[0]
                                num_bursts_Y = self._bursts.where(self._bursts['keyword'] == word_Y).dropna().shape[0]
                                NRW = relation_weight_BX * ((freq_BX * num_bursts_X) / tot_burst_len[word_X]) * (
                                            (freq_BY * num_bursts_Y) / tot_burst_len[word_Y])

                            elif formula == 'marzo2019_1':
                                # freq(Y, Bj) / length of the single burst of Y under examination (i.e. BYj)
                                BYj_len = self._single_burst_length(burst_Y_j)
                                NRW = relation_weight_BX * (freq_BX / tot_burst_len[word_X]) * (freq_BY / BYj_len)

                            elif formula == 'marzo2019_2':
                                # similar to the previous but also for BXi
                                BXi_len = self._single_burst_length(burst_X_i)
                                BYj_len = self._single_burst_length(burst_Y_j)
                                NRW = relation_weight_BX * (freq_BX / BXi_len) * (freq_BY / BYj_len)


                            # update the final matrix
                            # (i.e. sum the NRW between the current burst of word X
                            # and its related burst of word Y to the already stored weight between word X and word Y)
                            self._burst_norm.at[word_X, word_Y] += NRW

    def _total_length(self, keyword):
        """Finds the total length of all bursts of a keyword"""

        tot_len = 0

        sub_df = self._bursts.where(self._bursts['keyword'] == keyword).dropna()

        for i, r in sub_df.iterrows():
            tot_len += (sub_df.loc[i]["end"] - sub_df.loc[i]["start"]) + 1

        """"
        tot_len = (self._burst_results.where(self._burst_results['keyword'] == keyword).sum()['end'] -
                   self._burst_results.where(self._burst_results['keyword'] == keyword).sum()['start'])
        """

        return tot_len

    def _single_burst_length(self, burst_id):
        """

        :param burst_id:
        :return:
        """

        sub_df = self._bursts.loc[burst_id]
        length = sub_df['end'] - sub_df['start'] + 1

        return length

    def _total_length_related(self, x, y):
        """
        Finds the total length of bursts of y that have a relation with some burst of x.
        :param x:
        :param y:
        :return: length (int)
        """

        sub_df = self._burst_pairs[(self._burst_pairs["x"] == x) & (self._burst_pairs["y"] == y)]
        # delete duplicate bursts of Y
        sub_df = sub_df.drop_duplicates(['By_start', 'By_end'])
        length = sub_df['By_end'].sum() - sub_df['By_start'].sum() + sub_df.shape[0]

        return length

    #def _word_frequency(self, keyword, start, end, occ_index_file: str=None):
    def _word_frequency(self, keyword, start, end, sents_idx):
        """
        Finds the frequency of a keyword in the portion of text between the limits of a burst.

        :param occ_index_file:
        """

        freq = 0

        #if occ_index_file is not None:
        if sents_idx is not None:
            # use the occurrences provided in the index file to compute frequencies
            '''sents_idx = pd.read_csv(occ_index_file,
                                    index_col=0,
                                    usecols=["Lemma", "idFrase", "idParolaStart"],
                                    encoding="utf-8", sep="\t")'''
            # TODO: improve readability using .loc[[keyword]] that always returns a dataframe and thus avoid problems with .shape[0]
            #if type(sents_idx.loc[keyword]) == pd.Series:
            if type(sents_idx.loc[sents_idx['Lemma'] == keyword]) == pd.Series:
                # there is only one occurrence
                freq = 1
            else:
                occs_in_burst = sents_idx.loc[sents_idx['Lemma'] == keyword][(sents_idx.loc[sents_idx['Lemma'] == keyword].idFrase >= start) &
                                                   (sents_idx.loc[sents_idx['Lemma'] == keyword].idFrase <= end)]
                freq = occs_in_burst.shape[0]
        '''else:
            # occurrences are not provided: use NLTK to compute frequencies
            # TODO SE2020: questa parte non dovrebbe servire in PRET
            with open(self._text_filename, 'r', encoding='utf-8') as text:
                splitted_text = nltk.sent_tokenize(str(text.read()))

                for sent in splitted_text[start:end + 1]:
                    freq += sent.upper().count(keyword.upper())'''

        return freq


    @property
    def burst_results(self):
        """Getter"""
        return self._bursts

    @property
    def burst_weight_matrix(self):
        """Getter"""
        return self._burst_weight_matrix

    @property
    def burst_norm(self):
        """Getter of the final dataframe with normalized weights"""
        return self._burst_norm
