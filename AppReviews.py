import numpy as np
import pandas as pd
import requests

def single_country_reviews(
    appID, 
    country='us', 
    page=1, 
    df=pd.DataFrame()):
    """
    Gets pandas DataFrame of app store reviews based on an ID

    ARGUMENTS
    ----------
    appID: int
        apple ID of the app. Generally 9 digit number
        Can be found in the url of a store page after "/id="
    Country: string of length 2
        apple country ID
        the list of country IDs can be found in a dict
    RETURNS:
    ---------
    Pandas DataFrame formatted: 
        [title, game version, rating, review, review votes]

    INTERNAL ARGUMENTS:
    -------------------
    page: int
        Page number to start the request at
        Looks recursively until it cannot find a page

    df: pandas DataFrame
        dataframe from previous page. final df is appended from each page        
    """
    url = 'https://itunes.apple.com/' + country \
          + '/rss/customerreviews/id=%s/page=%d/sortby=mostrecent/json' \
          % (appID, page)

    req = requests.get(url)

    try:
        data = req.json().get('feed')
        page_error = False
    except ValueError:
        return df.reset_index(drop=True)

    try:
        df_index = np.arange(len(data.get('entry')))
    except:
        return df.reset_index(drop=True)

    csvTitles = ['title', 'version', 'rating', 'review', 'vote_count']
    page_df = pd.DataFrame(index=df_index, columns=csvTitles)

    entry_index = -1  # DataFrame Index

    for entry in data.get('entry'):
        if entry.get('im:name'):
            continue
        entry_index += 1
        page_df.title.loc[entry_index] = entry.get('title').get('label')
        page_df.version.loc[entry_index] = entry.get('im:version').get('label')
        page_df.rating.loc[entry_index] = entry.get('im:rating').get('label')
        page_df.review.loc[entry_index] = entry.get('content').get('label')
        page_df.vote_count.loc[entry_index] = entry.get('im:voteCount').get(
            'label')
    
    # Clean up returned values
    page_df.dropna(axis=0, how='all', inplace=True)
    page_df.fillna({'title' : '', 'review' : '', 'version': ''})
    page_df.rating = pd.to_numeric(page_df.rating, 
                                   downcast='unsigned', 
                                   errors='coerce')
    page_df.vote_count = pd.to_numeric(page_df.vote_count, 
                                       downcast='unsigned', 
                                       errors='coerce')
    
    
    if not page_error:
        return single_country_reviews(
            appID,
            country=country,
            page=page + 1,
            df=df.append(page_df).reset_index(drop=True))


def get_reviews(
    appID, 
    list_countries=list('us', 'gb', 'ca', 'au', 'ie', 'nz')):
    """
    Gets single pandas dataframe from multiple countries

    ARGUMENTS
    ----------
    appID: int
        apple ID of the app. Generally 9 digit number
        Can be found in the url of a store page after "/id="
    Country: list of apple country ID strings
        the list of country IDs can be found in a dict
    RETURNS:
    ---------
    Pandas DataFrame formatted: 
        [title, game version, rating, review, review votes]   
    """
    if type(list_countries) == str:
        list_countries = [list_countries]
        
    df = pd.DataFrame()
    
    for country in list_countries:
        df=df.append(
            single_country_reviews(appID, country=country)
            ).reset_index(drop=True)
    return df