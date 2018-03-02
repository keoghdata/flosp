#### script provides class defintions for hospital data project.
# seperate scripts provided in F* files for now which are imported seperately.
import pandas as pd
from expected_file_structures import *

class hosp(object):
    """ Class to manage hospital data importing.
    Input: name, string, for all file prefixs.
    """
    def __init__(self,name):
        print('-'*40)
        print('Created hosp class instance: ', name)
        print('-'*40)
        # make dict for passing down class heirarcy
        meta_info = {
        '_name': name,
        '_pathCLEAN': './../../3_Data/processed/',
        '_pathOUTPUT': './../../6_Outputs/',
        '_dataRAW_expected_dtypes':dataRAW_expected_dtypes,
        '_dataRAW_expected_cols':list(dataRAW_expected_dtypes.keys()),
        '_dataframes_list':dataframes_list
        }

        # import expected file structure data
        # dataRAW_expected_dtypes #dict of cols:dtypes
        # list(dataRAW_expected_dtypes.keys()) #list columns of above
        # dataframes_list # list of possible dataframes


        self._unpack_meta(meta_info)

        #### instantiate class heirarcy
        self.ioED = ioED(meta_info)
        self.ioIP = ioIP(meta_info)
        self.pat = pat(meta_info)
        self.daily = daily(meta_info)
        self.weekly = weekly(meta_info)


    def _unpack_meta(self, meta_info):
        """ place each meta item as attribute of class """
        for key, value in meta_info.items():
            setattr(self, key, value)

    def _loadPKL(self, path_to,attribute_name):
        """ find clean pkl file and load
        input
        path_to: str, location of pkl
        attribute_name: str, name to store under
        """
        x = pd.read_pickle(path_to) # read pkl to df
        setattr(self, attribute_name, x) # save to attribute

    def _searchFILE(self, path, filenames):
        """
        looks for filelist matching (filename), in folder (path), if not print not found. Retunr list of founds.
        Input
        path: str, path to folder
        filenames: list of str, filenames to find
        """
        from os.path import exists
        avail_files = []
        for i in filenames:
            if exists(path + i):
                print('Found: ',i)
                avail_files.append(path+i)
            else:
                print('Missing: ', i)

        return avail_files

    def _loadCLEAN(self):
        ## look for filelist, if present load, if not print not found. Retunr list of founds.
        poss_files = [
        self._name + 'ED' + self._period + '.pkl',
        self._name + 'IP'+ self._period + '.pkl'
        ]

        files = self._searchFILE(self._pathCLEAN,poss_files)
        #call load on list that is retuned
        for i in files:
            # get attribute name 'ED' or 'IP' from filename
            attrib_name = i.split('/')[-1].split('.')[0][len(self._name):-len(self._period)]
            attrib_name = '_'+ attrib_name
            # load data and assign to attribute
            self._loadPKL(i,attrib_name)

    def _loadRAW(self):
        ## look for filelist, if present load, if not print not found. Retunr list of founds.
        poss_files = [
        self._name + 'ED' + self._period + '.pkl',
        self._name + 'IP'+ self._period + '.pkl'
        ]
        self._pathRAW = self._pathCLEAN + 'RAW/'
        files = self._searchFILE(self._pathRAW,poss_files)
        #call load on list that is retuned
        for i in files:
            # get attribute name 'ED' or 'IP' from filename
            attrib_name = i.split('/')[-1].split('.')[0][len(self._name):-len(self._period)]
            attrib_name = '_'+ attrib_name
            # load data and assign to attribute
            self._loadPKL(i,attrib_name)

    def _searchATTRIBUTE(self):
        attribute_list = []
        for i in self._dataframes_list:
            if hasattr(self, i):
                attribute_list.append(i)
        return attribute_list

    def _savePKL(self, path, attribute_list):
        """
        save dfs as pkls given list of attributes and path
        """
        for i in attribute_list:
            df = getattr(self,i)
            dt_period = i[7:] # get EDpat, IPday part of name
            fullfilepath = path + self._name + dt_period + '.pkl'
            df.to_pickle(fullfilepath)
            print(self._name + dt_period + '.pkl')

    def get_pathCLEAN(self):
        return self._pathCLEAN

    def status(self):
        """
        Method to print details about class instance.
        """
        print(40*'-')
        print('Name of data: ' + self._name)
        print()
        print('Datas currently loaded:')
        for i in self._dataframes_list:
            present = check_presence_df(self,i)
            if present == True:
                print(i)
        return



    def __str__(self):
        return 'info about class instance'

class ioED(hosp):
    """ Tools for io of ED data.
    Workflow:
    1) import hosp csv with: load_hosp_csv
    2) use tools/manually transform df to standard columns types (use checks method).
    3) create daily and with:
    4) save as RAW to stage changes at any time: saveRAWasRAW
    5) once cleaned: saveRAWasCLEAN (files will then autoload in other parts of hospital class)
    """
    def __init__(self, meta_info):
        self._unpack_meta(meta_info)
        self._location = 'ED'
        pass

    def loadCLEAN(self):
        self._loadCLEAN()

    def loadRAW(self):
        self._loadRAW()

    def load_hosp_csv(self,path,col_mapping):
        """
        Function imports ED data and extracts columns of interest into generic column namings.

        Inputs
        path: string, path to RAW ED csv file
        cols_select: dict, dictionary of columns to use {'name of col in input df':'new column name'}

        Output
        Pandas dataframe of ED patient level data.
        """
        print('-'*40)
        #print(loadRAW)
        #### import dataframe
        print('importing raw ED data to dataframe')
        print('-'*40)
        df = pd.read_csv(path,
        low_memory=False)

        #### tidy column names
        #from Fcleaning import pd_tidy_column_heads
        df = pd_tidy_column_heads(df) # how do i call this inslide function?
        #### select columns
        if col_mapping == None:
            print('No columns mappings provided!')
            # should add a check here that all the column names are required
        else:
            print('User defined columns provided.')
        # rename columns to standard format
        df.rename(columns = col_mapping,inplace=True)
        df = df[list(col_mapping.values())]
        self._dataRAW = df
        print('Raw data loaded.')
        return #df

    def checks(self):
        """
        Run all checks we currently have on current RAW progress.
        """
        print('-'*40)
        print('Running checks on RAW df...')
        print('-'*40)
        self.status()
        for i in self._dataframes_list:
            if check_presence_df(self,i) == True:
                ## list columns that are missing
                x1 = getattr(self, i)
                x1 = set(x1.columns)
                x2 = set(self._dataRAW_expected_cols)
                if len(list(x2 - x1)) >= 1:
                    print('Missing columns: ' , list(x2 - x1))
                else:
                    print('Columns present.')
                    ## call funct to check datatypes after we know all cols in place!
                    check_column_dtypes(self, i)
        # check_missing func?
        print()
        print('Checks complete.')

        return


    def get_EDraw(self):
        """ retrieve raw ED data, returns df """
        # possible selection wiht keyword?
        return self._dataRAW

    def replace_EDraw(self, x):
        """ replace EDraw data with new df (input) """
        self._dataRAW = x
        return

    def status(self):
        """ print various statments about raw data """
        print('-'*20)
        print('Status of RAW data ')
        print('-'*20)
        print('dataframe shape: ', self._dataRAW.shape)

    def create_auto_columns(self):
        """
        Function creates additional colums which are automatic as names are standardised inc:
        - waiting time (minutes)
        - breach flag
        - callender columns
        """
        #### create waitingtime column
        self._dataRAW = make_waitingtime_column(self._dataRAW)
        #### create breach flags
        self._dataRAW['breach_flag'] = (self._dataRAW['waiting_time'] > 4*60).astype(int)
        #### create: day of week, time of day, month of year columns
        self._dataRAW = make_callender_columns(self._dataRAW,'arrival_datetime','arr')
        self._dataRAW = make_callender_columns(self._dataRAW,'leaving_datetime','leaving')

    def create_aggregates(self):
        """ create daily, weekly and monthly transforms of data. RAW patient level data will need to be in standard format before running this is problems not to occur!
        """
        self._dataR_EDday = create_dailyED(self._dataRAW)

    def transform(self):
        pass

    def saveRAWasRAW(self):
        """ save the raw files as .pkl in the processed folder specified """
        self._dataR_EDpat = self._dataRAW #move patinet lvl data to this attribute for saving
        print('-'*40)
        print('Saving RAW as pkls in RAW folder...')
        raw_df_list = self._searchATTRIBUTE()
        if len(raw_df_list) == 0:
            print('No RAW files to save.')
        else:
            path = self._pathCLEAN + 'RAW/'
            self._savePKL(path,raw_df_list)

        print('Save complete.')
        return

    def saveRAWasCLEAN(self):
        """ save the raw files as .pkl in the processed folder specified. Do once happy that data is all clean. """
        self._dataR_EDpat = self._dataRAW #move patinet lvl data to this attribute for saving
        print('-'*40)
        print('Saving RAW as pkls in CLEAN folder...')
        raw_df_list = self._searchATTRIBUTE()
        if len(raw_df_list) == 0:
            print('No RAW files to save.')
        else:
            path = self._pathCLEAN
            self._savePKL(path,raw_df_list)

        print('Save complete.')
        return


class ioIP(hosp):
    """ """
    def __init__(self, meta_info):
        pass

class pat(hosp):
    """
    #! if cna figure out generalised plots, then import seperate plotting scripts, and modify the calls for each (e.g. different column calls)
    """
    def __init__(self, meta_info):
        self._period = 'pat'
        self._unpack_meta(meta_info)
        print('-'*20)
        print('Patient fileload: ')
        print('-'*20)
        self._loadCLEAN()

    def loadCLEAN(self):
        self._loadCLEAN()



    def get_ED(self):
        """ return ED df """
        return self._ED

    def get_IP(self):
        """ return ED df """
        return self._ED

class daily(hosp):
    def __init__(self, meta_info):
        self._period = 'daily'
        self._unpack_meta(meta_info)
        print('-'*20)
        print('Daily fileload: ')
        print('-'*20)
        self._loadCLEAN()

    def loadCLEAN(self):
        self._loadCLEAN()

    def create_daily(self):
        pass



class weekly(hosp):
    def __init__(self,meta_info):
        self._unpack_meta(meta_info)
        pass
    def testPLOTw(self):
        pass

    def create_weekly(self):
        pass

######################################################
#### seperate functions ####
######################################################

def make_callender_columns(x,column,prefix):
    """
    Function to take a datetime column and create: hour of day, day of week, month of year columns.
    Input
    x(df): dataframe
    column (string): name of datetime column to work from
    prefix (string): give prefix for column names

    Output
    x(df): new df with additional columns with numerical indicators for callender vars.
    """
    print('-'*40)
    print(make_callender_columns)
    x[prefix + '_hour'] = x[column].dt.hour.astype(object)
    x[prefix + '_dayofweek'] = x[column].dt.dayofweek.astype(object)
    x[prefix + '_month'] = x[column].dt.month.astype(object)
    return(x)

def pd_tidy_column_heads(x):
    """
    Function makes all column names lowercase and replaces any whitespace with _'s. Removes wild characters.

    Input
    df for cleaning

    Returns
    tidy dataframe for assignment to variable name
    """
    rename_cols = dict() # make dictionary of old column names and new ones
    for i in x.columns:
        j = i.lower()
        j = j.strip()
        j = j.replace(' ','_')
        j = j.replace('.','_')
        j = j.replace('?','_')
        j = j.replace('&','_')
        j = j.replace('%','perc')
        j = j.replace('(','')
        j = j.replace(')','')
        j = j.replace(':','')
        j = j.replace(';','')
        j = j.replace('-','')
        j = j.replace('/','')
        #j = j.replace('\','')
        rename_cols[i] = j

    x = x.rename(columns=rename_cols)
    return(x)


def check_presence_df(x,df_name):
    """
    check if dataframe present
    """
    if hasattr(x, df_name):
        present = True
    else:
        present = False
    return present


def check_column_dtypes(x,df,exp_dict = '_dataRAW_expected_dtypes'):
    """
    Take df argument and check if dtypes match expected for RAW.
    Input
    df: attribute pointer for df to check
    exp_dict: dict, columns and expected datatypes.

    Output

    """
    df_dtypes = getattr(x,exp_dict)
    df = getattr(x,df)

    for j in df.columns:
        if df[j].dtypes != df_dtypes[j]:
            print('Col ', j, ' is of dtype:',df[j].dtypes,'. Expected: ', df_dtypes[j])

    return


def create_datetime_col(x):
    """
    Function creates datetime column from separate date and time columns.
    Input: df
    Output: df with additional columns
    """
    print('-'*40)
    print('create_datetime_col')
    print('-'*40)
    # Create arrival datetime column
    print('Creating arrival datetime column...(make take some time)')
    f = lambda i: pd.to_datetime(i.arrival_date + ' ' + i.arrival_time)
    x['arrival_datetime'] = x.apply(f,axis=1)

    #Create dishcarge datetime column
    print('Creating leaving datetime column...(make take some time)')
    f = lambda j: pd.to_datetime(j.arrival_date + ' ' + j.leaving_time)
    x['leaving_datetime'] = x.apply(f,axis=1)

    # correct negative stay times in ED (these are people who have rolled past midnight). There is an assumption here that LOS !> 24hours
    datetime_values = x[(x.leaving_datetime - x.arrival_datetime) < pd.Timedelta(0)].leaving_datetime + pd.Timedelta('1 days')

    x.leaving_datetime.iloc[datetime_values.index] = datetime_values.values

    #### there are 8 people who were in there for > 24 hours. we have no way of picking up how long they were in there.
    #df[(df.discharge_time - df.arrival_time) == pd.Timedelta('1 days')].shape

    return(x)


def make_waitingtime_column(x):
    """
    Function to create datetime column with arrival and discharge datetime columns
    Input: df of rawED data
    Ouput: new df with additional column of waiting time in minutes
    """
    print('-'*40)
    print(make_waitingtime_column)
    x['waiting_time'] = (x['leaving_datetime'] - x['arrival_datetime']) / pd.Timedelta('1 minute')
    return(x)

def create_dailyED(x):
    """
    create new df at daily level from patient level.

    input: df, x
    output: df, dailyED
    """
    ##### First need to calculate waiting times (split over days for calc of how mnay ED waiting minutes there were)
    ##### possible that should move this upstream at later stage so available to pat level df.
    df = x

    def minutes_in_ED_today(x):
        if x.arrival_datetime.date() == x.leaving_datetime.date():
            y = x.waiting_time
        else:
            y = (24*60) - (x.arrival_datetime.hour*60 + x.arrival_datetime.minute)
        return(y)

    print(df.columns)

    df['minutes_today'] = df.apply(minutes_in_ED_today,axis=1)

    def minutes_in_ED_tomo(x):
        if x.arrival_datetime.date() != x.leaving_datetime.date():
            y = x.leaving_datetime.minute + x.leaving_datetime.hour*60
        else:
            y = 0
        return(y)

    df['minutes_tomo'] = df.apply(minutes_in_ED_tomo,axis=1)

    # check total waiting times match up
    if df[['minutes_tomo','minutes_today']].sum().sum() != df['waiting_time'].sum():
        print('WARNING: problem with aggregating minutes over days.')
        print(df[['minutes_tomo','minutes_today']].sum().sum())
        print(df['waiting_time'].sum())

    # calc: arrival numbers, median age

    df_gb = df[['arrival_datetime','age','minutes_today']]

    agg_dic = {'arrival_datetime':'count'
                ,'age':'median'
              ,'minutes_today':'sum'
              }

    daily1 = df_gb.groupby(by=[df_gb['arrival_datetime'].dt.date]).agg(agg_dic)

    #calc: discharges + admissions
    df_gb = df[['leaving_datetime','age','adm_flag','minutes_tomo']]

    agg_dic = {'leaving_datetime':'count'
               ,'adm_flag':'sum'
               ,'minutes_tomo':'sum'
                }

    daily2 = df_gb.groupby(by=[df_gb['leaving_datetime'].dt.date]).agg(agg_dic)
    #daily2.head()

    #calc: breaches counts - this should be lifted updwards!
    df['breach_datetime'] = df.arrival_datetime + pd.Timedelta('4 hour')

    df_gb = df[['breach_datetime','breach_flag']]

    agg_dic = {'breach_flag':'sum'
                }

    daily3 = df_gb.groupby(by=[df_gb['breach_datetime'].dt.date]).agg(agg_dic)
    #daily3.head(5)

    #cal total number of minutes waiting each day?

    # merge each of daily dfs created

    daily1.shape

    daily2.shape

    daily = pd.merge(daily1,daily2,left_index=True, right_index=True,how='outer')
    daily.shape

    daily3.shape

    daily = pd.merge(daily,daily3,left_index=True,right_index=True,how='outer')
    daily.shape


    # make total minutes used in ED column
    daily['minutes_used'] = daily.minutes_today + daily.minutes_tomo
    daily.shape
    daily.drop(['minutes_today','minutes_tomo'],axis=1,inplace=True)
    daily.shape

    # rename columns sensibly
    #daily.columns
    daily.rename(columns={'arrival_datetime':'arrivals','leaving_datetime':'discharges','age':'age_median',
                         'adm_flag':'admissions','breach_flag':'breaches'},inplace=True)
    daily.head()
    daily['mean_patient_minutes'] = daily.minutes_used/daily.arrivals

    #### !! print wanring if we are missing dates, check that in reshape daily df was correct size
    # check for missing dates
    daily.shape
    daily.reindex().shape
    daily.isnull().sum()

    # create other vars of interest from daily
    daily['conversion_ratio'] = daily.admissions/daily.arrivals
    daily['breaches_perc'] = daily.breaches/daily.arrivals

    return daily
