import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

def feature_plot(features):
    labels= list(features)[:]
    stats= features.mean().tolist()
    angles=np.linspace(0, 2*np.pi, len(labels), endpoint=False)

    # close the plot
    stats=np.concatenate((stats,[stats[0]]))
    angles=np.concatenate((angles,[angles[0]]))

    #Size of the figure
    fig=plt.figure(figsize = (25,25))

    ax = fig.add_subplot(221, polar=True)
    ax.plot(angles, stats, 'o-', linewidth=2, label = "Features", color= 'grey')
    ax.fill(angles, stats, alpha=0.25, facecolor='purple')
    ax.set_thetagrids(angles[0:7] * 180/np.pi, labels , fontsize = 13)

    ax.set_rlabel_position(250)
    plt.yticks([0.25 , 0.5 , 0.75 , 1], ["0.25",'0.5', "0.75", "1"], color="grey", size=13)
    plt.ylim(0,1)

    plt.legend(loc='best', bbox_to_anchor=(0.1, 0.1))
    
    st.pyplot(plt)
    
def feature_plot2(features1,features2):
    labels= list(features1)[:]
    stats= features1.mean().tolist()
    stats2 = features2.mean().tolist()
    angles=np.linspace(0, 2*np.pi, len(labels), endpoint=False)
    
    # close the plot
    stats=np.concatenate((stats,[stats[0]]))
    stats2 =np.concatenate((stats2,[stats2[0]])) 
    angles=np.concatenate((angles,[angles[0]]))

    #Size of the figure
    fig=plt.figure(figsize = (18,18))

    ax = fig.add_subplot(221, polar=True)
    ax.plot(angles, stats, 'o-', linewidth=2, label = "Original Selection", color= 'gray')
    ax.fill(angles, stats, alpha=0.25, facecolor='blue')
    ax.set_thetagrids(angles[0:7] * 180/np.pi, labels , fontsize = 13)

    ax.set_rlabel_position(250)
    plt.yticks([0.25 , 0.5 , 0.75 , 1], ["0.25",'0.5', "0.75", "1"], color="grey", size=13)
    plt.ylim(0,1)

    ax.plot(angles, stats2, 'o-', linewidth=2, label = "Our Recommendation", color = 'm')
    ax.fill(angles, stats2, alpha=0.25, facecolor='m' )
    ax.grid(True)

    plt.legend(loc='best', bbox_to_anchor=(0.095, 0.095))
    
    st.pyplot(plt)
