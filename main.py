import requests
import streamlit as st
import pandas as pd
import spotipy
import polarplot
import seaborn as sns
import songrecommendations
import matplotlib.pyplot as plt
from spotipy.oauth2 import SpotifyClientCredentials

SPOTIPY_CLIENT_ID='a9c08768bf6f4d5083cdafbbf17c2277'
SPOTIPY_CLIENT_SECRET='445ef713ee2b40d19c9c5d178f6b2380'

auth_manager = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
sp = spotipy.Spotify(auth_manager=auth_manager)

st.header('Predictive Song Analysis')
st.write("-------")

search_choices = ['Song', 'Artist', 'Album']
search_selected = st.sidebar.selectbox("Menu - Search By: ", search_choices)

st.subheader(f'What Is Your Favourite {search_selected}?')

search_keyword = st.text_input(search_selected + " Search Engine")
button_clicked = st.button("SEARCH")
st.write("___")

search_results = []
tracks = []
artists = []
albums = []

if search_keyword is not None and len(str(search_keyword)) > 0:
    if search_selected == 'Song':
        st.write("Choose Your Song From the Drop-Down Menu")
        tracks = sp.search(q='track:'+ search_keyword,type='track', limit=25)
        tracks_list = tracks['tracks']['items']
        if len(tracks_list) > 0:
            for track in tracks_list:
                search_results.append(track['name'] + " - By - " + track['artists'][0]['name'])
        
    elif search_selected == 'Artist':
        st.write("Start Artist Search")
        artists = sp.search(q='artist:'+ search_keyword,type='artist', limit=25)
        artists_list = artists['artists']['items']
        if len(artists_list) > 0:
            for artist in artists_list:
                search_results.append(artist['name'])
        
    if search_selected == 'Album':
        st.write("Start Album Search")
        albums = sp.search(q='album:'+ search_keyword,type='album', limit=25)
        albums_list = albums['albums']['items']
        if len(albums_list) > 0:
            for album in albums_list:
                search_results.append(album['name'] + " - By - " + album['artists'][0]['name'])

selected_album = None
selected_artist = None
selected_track = None

if search_selected == 'Song':
    selected_track = st.selectbox("Select Your Song: ", search_results)
elif search_selected == 'Artist':
    selected_artist = st.selectbox("Select Your Artist: ", search_results)
elif search_selected == 'Album':
    selected_album = st.selectbox("Select Your Album: ", search_results)

if selected_track is not None and len(tracks) > 0:
    tracks_list = tracks['tracks']['items']
    track_id = None
    if len(tracks_list) > 0:
        for track in tracks_list:
            str_temp = track['name'] + " - By - " + track['artists'][0]['name']
            if str_temp == selected_track:
                track_id = track['id']
                track_album = track['album']['name']
                img_album = track['album']['images'][1]['url']
                songrecommendations.save_album_image(img_album, track_id)                
                tracks = sp.search(q='track:'+ track['name'],type='track', limit=25)
                
    selected_track_choice = None            
    if track_id is not None:
        image = songrecommendations.get_album_mage(track_id)
        st.image(image, use_column_width=True)
        track_choices = ['Song Features']
        track_features  = sp.audio_features(track_id) 
        df = pd.DataFrame(track_features, index=[0])
        try:         
            st.audio(tracks['tracks']['items'][0]['preview_url'], format="audio/mp3")
        except:
            pass

        df2 = df.loc[:,['instrumentalness', 'liveness', 'acousticness', 'danceability', 'energy', 'speechiness', 'tempo', 'duration_ms', 'track_href']]
        df_features = df.loc[: ,['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'speechiness', 'valence']]
        st.dataframe(df2)
        polarplot.feature_plot(df_features)

        st.header('Analyzing Your Music Tastes ...')
        
        token = songrecommendations.get_token(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET)
        similar_songs_json = songrecommendations.get_track_recommendations(track_id, token)
        
        def trck_recc(seed_tracks,token):
            limit = 100
            recUrl = f"https://api.spotify.com/v1/recommendations?limit={limit}&seed_tracks={seed_tracks}"

            headers = {
                "Authorization": "Bearer " + token
            }

            res = requests.get(url=recUrl, headers=headers)
            return res.json()

        json_response2 = trck_recc(track_id,token)
        
        recc_track_result = []
        
        for i, item in enumerate(json_response2['tracks']):
            track = item['album']
            track_id = item['id']
            track_name = item['name']
            popularity = item['popularity']
            explicit = item['explicit']
            duration = ((item['duration_ms']/1000)/60)
            preview_url = item['preview_url']
            recc_track_result.append((track['artists'][0]['name'], track['name'], duration, track_name, track['release_date'], popularity, track_id, explicit, preview_url, i)) 
            
        recc_track_result_df = pd.DataFrame(recc_track_result, index=None, columns=('Artist', 'Song Name', 'Duration_mins', 'Album Name', 'Release Date', 'Popularity','Id','Explicit', 'Preview_url','item'))

        audio_features_df = pd.DataFrame()
        for id in recc_track_result_df['Id'].iteritems():
            track_id = id[1]
            audio_features = sp.audio_features(track_id)
            local_features = pd.DataFrame(audio_features, index=[0])
            audio_features_df = audio_features_df.append(local_features)      
                
        our_final_df = recc_track_result_df.merge(audio_features_df, left_on="Id", right_on="id")
        st.dataframe(our_final_df)
        
        
        corr = our_final_df[['Release Date', 'Popularity', 'Explicit', 'Duration_mins', 'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness',
            'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo']].corr()
        plt.figure(figsize=(20,13))
        fig = sns.heatmap(corr, annot = True, cmap="icefire_r") 
        
        st.pyplot(plt) 
        st.write(corr) 
     
        def bar_graphs():
            f1 = plt.figure(figsize=(15,13))      
            plt.subplot(331)
            sns.histplot(data=our_final_df, x="danceability",color='navy', kde = True, hue='Explicit', legend=False)
            plt.subplot(332)
            sns.histplot(data=our_final_df, x="loudness",color='navy', kde = True, hue='Explicit', legend=False)
            plt.subplot(333)
            sns.histplot(data=our_final_df, x="energy",color='navy', kde = True, hue='Explicit', legend=False)
            plt.subplot(334)
            sns.histplot(data=our_final_df, x="acousticness",color='navy', kde = True, hue='Explicit', legend=False)
            plt.subplot(335)
            sns.histplot(data=our_final_df, x="valence",color='navy', kde = True, hue='Explicit', legend=False)
            plt.subplot(336)
            sns.histplot(data=our_final_df, x="Popularity",color='navy', kde = True, hue='Explicit', legend=False)
            f2 = plt.figure(figsize=(15,13))   
            plt.subplot(331)
            sns.histplot(data=our_final_df, x="tempo",color='navy', kde = True, hue='Explicit', legend=False)
            plt.subplot(332)
            sns.histplot(data=our_final_df, x="Duration_mins",color='navy', kde = True, hue='Explicit', legend=False)
            plt.subplot(333)
            sns.histplot(data=our_final_df, x="key",color='navy', kde = True, hue='Explicit', legend=False)
            st.pyplot(f1)  
            st.pyplot(f2) 
        
        bar_graphs()
        
        def hist_graphs():
            f1 = plt.figure(figsize=(15,13))      
            plt.subplot(331)
            sns.histplot(data=our_final_df, x="loudness", y="energy", bins=15, discrete=(False, False), log_scale=(False, False), thresh=None,)
            plt.subplot(332)
            sns.histplot(data=our_final_df, x="valence", y="danceability", bins=15, discrete=(False, False), log_scale=(False, False), thresh=None,)
            plt.subplot(333)
            sns.histplot(data=our_final_df, x="acousticness", y="energy", bins=15, discrete=(False, False), log_scale=(False, False), thresh=None,)
            plt.subplot(334)
            sns.histplot(data=our_final_df, x="acousticness", y="loudness", bins=15, discrete=(False, False), log_scale=(False, False), thresh=None,)
            plt.subplot(335)
            sns.histplot(data=our_final_df, x="Duration_mins", y="energy", bins=15, discrete=(False, False), log_scale=(False, False), thresh=None,)
            plt.subplot(336)
            sns.histplot(data=our_final_df, x="Duration_mins", y="key", bins=15, discrete=(False, False), log_scale=(False, False), thresh=None,)     
            st.pyplot(f1)  
        
        hist_graphs()

        st.markdown(
        """
        Audio Feature Documentation:
        - Acousticness: the confidence measure from 0.0 to 1.0 of whether the track is acoustic. 1.0 represents high confidence that the track is acoustic.
        
        - Danceability: describes how suitable a track is for dancing based on a combination of musical elements including tempo, rhythm stability, beat strength, and overall regularity. A value of 0.0 is least danceable and 1.0 is most danceable.
        
        - Instrumentalness: predicts whether a track contains no vocals. "Ooh" and "aah" sounds are treated as instrumental in this context. Rap or spoken word tracks are clearly "vocal". The closer the instrumentalness value is to 1.0, the greater likelihood the track contains no vocal content. Values above 0.5 are intended to represent instrumental tracks, but confidence is higher as the value approaches 1.0.
        
        - Key: the key the track is in. Integers map to pitches using standard Pitch Class notation. E.g. 0 = C, 1 = C♯/D♭, 2 = D, and so on. If no key was detected, the value is -1.
                
        - Liveness: detects the presence of an audience in the recording. Higher liveness values represent an increased probability that the track was performed live. A value above 0.8 provides strong likelihood that the track is live.
        
        - Energy: measures from 0.0 to 1.0 and represents a perceptual measure of intensity and activity. Typically, energetic tracks feel fast, loud, and noisy. For example, death metal has high energy, while a Bach prelude scores low on the scale. Perceptual features contributing to this attribute include dynamic range, perceived loudness, timbre, onset rate, and general entropy.
        
        """
        )

        colls1,colls2,colls3 = st.columns(3)
        colls4,colls5,colls6 = st.columns(3)
        colls7,colls8,colls9 = st.columns(3)
        colls10,colls11,colls12 = st.columns(3)
        
        colls1.pyplot(sns.jointplot(data=our_final_df, x="danceability", y="Popularity",kind="reg", color='#03051A'))
        colls7.pyplot(sns.jointplot(data=our_final_df, x="acousticness", y="tempo", kind="kde", color='#03051A', cmap='rocket', fill=True, thresh=0))

        colls2.pyplot(sns.jointplot(data=our_final_df, x="Duration_mins", y="Popularity",kind="reg", color='#03051A'))
        colls8.pyplot(sns.jointplot(data=our_final_df, x="energy", y="loudness", kind="kde", color='#03051A', cmap='rocket', fill=True, thresh=0))

        colls3.pyplot(sns.jointplot(data=our_final_df, x="loudness", y="Popularity",kind="reg", color='#03051A'))
        colls9.pyplot(sns.jointplot(data=our_final_df, x="speechiness", y="Explicit", kind="kde", color='#03051A', cmap='rocket', fill=True, thresh=0))

        colls4.pyplot(sns.jointplot(data=our_final_df, x="tempo", y="Popularity",kind="reg", color='#03051A'))
        colls10.pyplot(sns.jointplot(data=our_final_df, x="loudness", y="valence", kind="kde", color='#03051A', cmap='rocket', fill=True, thresh=0))

        colls5.pyplot(sns.jointplot(data=our_final_df, x="energy", y="Popularity",kind="reg", color='#03051A'))
        colls11.pyplot(sns.jointplot(data=our_final_df, x="instrumentalness", y="Popularity", kind="kde", color='#03051A', cmap='rocket', fill=True, thresh=0))

        colls6.pyplot(sns.jointplot(data=our_final_df, x="speechiness", y="Popularity",kind="reg", color='#03051A'))      
        colls12.pyplot(sns.jointplot(data=our_final_df, x="danceability", y="speechiness", kind="kde", color='#03051A', cmap='rocket', fill=True, thresh=0))

        Nlst = []
        for i in df['id']:
            Nlst.append(i)
        Nlst2 = []
        for songs in similar_songs_json['tracks']:
            Nlst2.append(songs['name'])
        Nlst3 = []
        for songs in similar_songs_json['tracks']:
            Nlst3.append(songs['preview_url'])
            
    
        st.markdown(
        """
        - Loudness: the overall loudness of a track in decibels (dB). Loudness values are averaged across the entire track and are useful for comparing relative loudness of tracks. Loudness is the quality of a sound that is the primary psychological correlate of physical strength (amplitude). Values typically range between -60 and 0 db.
        
        - Tempo: the estimated tempo of a track in beats per minute (BPM). In musical terminology, tempo is the speed or pace of a given piece and derives directly from the average beat duration.
        
        - Time Signature: an estimated time signature. The time signature (meter) is a notational convention to specify how many beats are in each bar (or measure). The time signature ranges from 3 to 7 indicating time signatures of "3/4", to "7/4".
        
        - Mode: mode indicates the modality (major or minor) of a track, the type of scale from which its melodic content is derived. Major is represented by 1 and minor is 0.
        
        - Speechiness: detects the presence of spoken words in a track. The more exclusively speech-like the recording (e.g. talk show, audio book, poetry), the closer to 1.0 the attribute value. Values above 0.66 describe tracks that are probably made entirely of spoken words. Values between 0.33 and 0.66 describe tracks that may contain both music and speech, either in sections or layered, including such cases as rap music. Values below 0.33 most likely represent music and other non-speech-like tracks.
        
        - Valence: measures from 0.0 to 1.0 describing the musical positiveness conveyed by a track. Tracks with high valence sound more positive (e.g. happy, cheerful, euphoric), while tracks with low valence sound more negative (e.g. sad, depressed, angry).
        """
        )
    
        st.header('Recommendations Based on Your Search')
        token = songrecommendations.get_token(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET)
        similar_songs_json = songrecommendations.get_track_recommendations(track_id, token)
        recommendation_list = similar_songs_json['tracks']
        recommendation_list_df = pd.DataFrame(recommendation_list)
        recommendation_list_df2 = recommendation_list_df
        recommendation_df = recommendation_list_df[['name', 'popularity', 'duration_ms', 'explicit', 'href', 'available_markets']]
        recommendation_list_df2['duration_min'] = (round(recommendation_list_df2['duration_ms'] / 1000, 0))/60
        recommendation_list_df2["popularity_range"] = recommendation_list_df2["popularity"] - (recommendation_list_df2['popularity'].min() - 1)
        recommendation_list_df2 = recommendation_list_df2[['name', 'popularity', 'duration_min', 'explicit', 'href', 'available_markets']]
        st.dataframe(recommendation_list_df2)
        songrecommendations.song_recommendation_vis(recommendation_df)
 
        st.subheader(f'Your Next Favourite Song: {Nlst2[0]}')  
    
        track_audio_specs2  = sp.audio_features(Nlst[0])
        df5 = pd.DataFrame(track_audio_specs2, index=[0])
        df_audio_specs2 = df5.loc[:,['danceability', 'energy', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence']]
        polarplot.feature_plot2(df_features,df_audio_specs2) 
        
        try:
            for i in range(len(Nlst)):
                if Nlst3[i] != False and Nlst3[i] != '' and Nlst3[i] !=None:
                    st.text(Nlst[i])
                    st.audio(Nlst3[i], format="audio/mp3") 
            
        except:
            st.text('Bash Out')
            st.text('5wZK0hHduZpjWWoT0rq9p4')
            st.audio('5wZK0hHduZpjWWoT0rq9p4', format="audio/mp3") 

    else:
        st.write("Please select a track from the list")       

elif selected_album is not None and len(albums) > 0:
    albums_list = albums['albums']['items']
    album_id = None
    album_uri = None    
    album_name = None
    if len(albums_list) > 0:
        for album in albums_list:
            str_temp = album['name'] + " - By - " + album['artists'][0]['name']
            if selected_album == str_temp:
                album_id = album['id']
                album_uri = album['uri']
                album_name = album['name']
    if album_id is not None and album_uri is not None:
        st.write("Collecting all the tracks for the album :" + album_name)
        album_tracks = sp.album_tracks(album_id)
        df_album_tracks = pd.DataFrame(album_tracks['items'])
        df_tracks_min = df_album_tracks.loc[:,
                        ['id', 'name', 'duration_ms', 'explicit', 'preview_url']]
        for idx in df_tracks_min.index:
            with st.container():
                col1, col2, col3, col4 = st.columns((4,4,1,1))
                col11, col12 = st.columns((8,2))
                col1.write(df_tracks_min['id'][idx])
                col2.write(df_tracks_min['name'][idx])
                col3.write(df_tracks_min['duration_ms'][idx])
                col4.write(df_tracks_min['explicit'][idx])   
                if df_tracks_min['preview_url'][idx] is not None:
                    col11.write(df_tracks_min['preview_url'][idx])  
                    with col12:   
                        st.audio(df_tracks_min['preview_url'][idx], format="audio/mp3")                            
                                      
if selected_artist is not None and len(artists) > 0:
    artists_list = artists['artists']['items']
    artist_id = None
    artist_uri = None
    selected_artist_choice = None
    if len(artists_list) > 0:
        for artist in artists_list:
            if selected_artist == artist['name']:
                artist_id = artist['id']
                artist_uri = artist['uri']
    
    if artist_id is not None:
        artist_choice = ['Albums', 'Top Songs']
        selected_artist_choice = st.sidebar.selectbox('Select artist choice', artist_choice)
                
    if selected_artist_choice is not None:
        if selected_artist_choice == 'Albums':
            artist_uri = 'spotify:artist:' + artist_id
            album_result = sp.artist_albums(artist_uri, album_type='album') 
            all_albums = album_result['items']
            col1, col2, col3 = st.columns((6,4,2))
            for album in all_albums:
                col1.write(album['name'])
                col2.write(album['release_date'])
                col3.write(album['total_tracks'])
        elif selected_artist_choice == 'Top Songs':
            artist_uri = 'spotify:artist:' + artist_id
            top_songs_result = sp.artist_top_tracks(artist_uri)
            for track in top_songs_result['tracks']:
                with st.container():
                    col1, col2, col3, col4 = st.columns((4,4,2,2))
                    col11, col12 = st.columns((10,2))
                    col21, col22 = st.columns((11,1))
                    col31, col32 = st.columns((11,1))
                    col1.write(track['id'])
                    col2.write(track['name'])
                    if track['preview_url'] is not None:
                        col11.write(track['preview_url'])  
                        with col12:   
                            st.audio(track['preview_url'], format="audio/mp3")  
                    with col3:
                        def feature_requested():
                            track_features  = sp.audio_features(track['id']) 
                            df = pd.DataFrame(track_features, index=[0])
                            df_features = df.loc[: ,['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'speechiness', 'valence']]
                            with col21:
                                st.dataframe(df_features)
                            with col31:
                                polarplot.feature_plot(df_features)
                            
                        feature_button_state = st.button('Track Audio Features', key=track['id'], on_click=feature_requested)
                    with col4:
                        def similar_songs_requested():
                            token = songrecommendations.get_token(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET)
                            similar_songs_json = songrecommendations.get_track_recommendations(track['id'], token)
                            recommendation_list = similar_songs_json['tracks']
                            recommendation_list_df = pd.DataFrame(recommendation_list)
                            recommendation_df = recommendation_list_df[['name', 'explicit', 'duration_ms', 'popularity']]
                            with col21:
                                st.dataframe(recommendation_df)
                            with col31:
                                songrecommendations.song_recommendation_vis(recommendation_df)

                        similar_songs_state = st.button('Similar Songs', key=track['name'], on_click=similar_songs_requested)
                    st.write('----')
