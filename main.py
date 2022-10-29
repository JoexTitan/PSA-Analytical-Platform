import streamlit as st
import pandas as pd

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import polarplot
import songrecommendations

SPOTIPY_CLIENT_ID='a9c08768bf6f4d5083cdafbbf17c2277'
SPOTIPY_CLIENT_SECRET='445ef713ee2b40d19c9c5d178f6b2380'

auth_manager = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
sp = spotipy.Spotify(auth_manager=auth_manager)

st.header('Spotify Song Analytics')

search_choices = ['Song', 'Artist', 'Album']
search_selected = st.sidebar.selectbox("Menu - Search By: ", search_choices)

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
    selected_track_choice = None            
    if track_id is not None:
        image = songrecommendations.get_album_mage(track_id)
        st.image(image, use_column_width=True)
        track_choices = ['Song Features']

        track_features  = sp.audio_features(track_id) 
        df = pd.DataFrame(track_features, index=[0])

        st.audio(tracks_list[0]['preview_url'], format="audio/mp3")  
        df2 = df.loc[:,['instrumentalness', 'liveness', 'acousticness', 'danceability', 'energy', 'speechiness', 'tempo', 'duration_ms', 'track_href']]
        df_features = df.loc[: ,['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'speechiness', 'valence']]
        st.dataframe(df2)
        polarplot.feature_plot(df_features)
        st.header('Top Recommendations Based on Your Search')
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
        
        
        #######   
        
        st.markdown(
        """
        Audio Features Documentation:
        - Acousticness: the confidence measure from 0.0 to 1.0 of whether the track is acoustic. 1.0 represents high confidence that the track is acoustic.
        
        - Danceability: describes how suitable a track is for dancing based on a combination of musical elements including tempo, rhythm stability, beat strength, and overall regularity. A value of 0.0 is least danceable and 1.0 is most danceable.
        
        - Instrumentalness: predicts whether a track contains no vocals. "Ooh" and "aah" sounds are treated as instrumental in this context. Rap or spoken word tracks are clearly "vocal". The closer the instrumentalness value is to 1.0, the greater likelihood the track contains no vocal content. Values above 0.5 are intended to represent instrumental tracks, but confidence is higher as the value approaches 1.0.
        
        - Speechiness: detects the presence of spoken words in a track. The more exclusively speech-like the recording (e.g. talk show, audio book, poetry), the closer to 1.0 the attribute value. Values above 0.66 describe tracks that are probably made entirely of spoken words. Values between 0.33 and 0.66 describe tracks that may contain both music and speech, either in sections or layered, including such cases as rap music. Values below 0.33 most likely represent music and other non-speech-like tracks.
        
        - Valence: measures from 0.0 to 1.0 describing the musical positiveness conveyed by a track. Tracks with high valence sound more positive (e.g. happy, cheerful, euphoric), while tracks with low valence sound more negative (e.g. sad, depressed, angry).
        
        - Liveness: detects the presence of an audience in the recording. Higher liveness values represent an increased probability that the track was performed live. A value above 0.8 provides strong likelihood that the track is live.
        
        - Energy: measures from 0.0 to 1.0 and represents a perceptual measure of intensity and activity. Typically, energetic tracks feel fast, loud, and noisy. For example, death metal has high energy, while a Bach prelude scores low on the scale. Perceptual features contributing to this attribute include dynamic range, perceived loudness, timbre, onset rate, and general entropy.
        
        """
        )
  
        Nlst = []
        for i in df['id']:
            Nlst.append(i)
        Nlst2 = []
        for songs in similar_songs_json['tracks']:
            Nlst2.append(songs['name'])
        Nlst3 = []
        for songs in similar_songs_json['tracks']:
            Nlst3.append(songs['preview_url'])
            
        st.header('Predicting Your Next Favorite Song')  
    
        track_audio_specs2  = sp.audio_features(Nlst[0])
        df5 = pd.DataFrame(track_audio_specs2, index=[0])
        df_audio_specs2 = df5.loc[:,['danceability', 'energy', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence']]
        polarplot.feature_plot(df_audio_specs2) 
        
        try:
            for i in range(len(Nlst)):
                if Nlst3[i] != False and Nlst3[i] != '' and Nlst3[i] !=None:
                    st.text(Nlst2[i])
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
