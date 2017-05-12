# -*- coding: utf-8 -*-
"""
Created on Sat May  6 16:52:18 2017

@author: kisha_000
"""

import sys
import numpy as np


#preprocessing data - encoding the sequences that are going to be aligned
def preprocessing(N):

    dicio = {}
    
    with open("movies.txt",encoding='latin-1') as myfile:
        for i,line in enumerate(myfile):
            aux = line.split(":")
            if(aux[0] == 'product/productId'):
                product = aux[1]
            if(aux[0] == 'review/userId'):
                user = aux[1]
            if(aux[0] == 'review/score'):
                review = aux[1]
                seq = review[1] + '.' + product[1:-1]
                if(user[1:-1] in dicio):
                    dicio[user[1:-1]] = dicio[user[1:-1]] + ',' + seq
                else:
                    dicio[user[1:-1]] = seq
            if i>N:
                break
            
    return dicio
        


#Implementation of Needlman-Wunsch

match=1.
mismatch=-1.
#gap penalty
gap=0


# Initialisation of the score matrix
def score_initialisation(rows,cols):
    
            
    score=np.zeros((rows,cols),float)

    for i in range(rows):
        score[i][0] = -i*gap
    for j in range(cols):
        score[0][j] = -j*gap
             
    return score

# Initialisation of the traceback matrix
def traceback_initialisation(rows,cols):
    
            
    traceback=np.zeros((rows,cols))

    # end of path top left corner
    traceback[0][0] = -1

    #going up
    for i in range(1,rows):
        traceback[i][0] = 1 
    
    #going left
    for j in range(1,cols):
        traceback[0][j] = 2
             
    return traceback

    
# calculation of the scores and filling the traceback matrix
def calculate_scores(score,traceback,rows,cols,seq1,seq2):
    
 
    for i in range(1,rows):
        for j in range(1,cols):
            # Dynamic programing -- aka. divide and conquer:
            # Since gap penalties are linear in gap size
            # the score of an alignmet of length l only depends on the   
            # the l-th characters in the alignment (match - mismatch - gap)
            # and the score of the one shorter (l-1) alignment,
            # i.e. we can calculate how to extend an arbritary alignment
            # soley based on the previous score value.  
            rating_penalty = (abs(float(seq2[i-1][0])-float(seq1[j-1][0])))/5
            
            if(seq1[j-1][1] == seq2[i-1][1]):
                s_function = match
            else:
                s_function = mismatch
                
           # choice1 = score[i-1][j-1] + s[(seq1[j-1][1] + seq2[i-1][1])] - rating_penalty
            choice1 = score[i-1][j-1] + s_function - rating_penalty
            choice2 = score[i-1][j] - gap
            choice3 = score[i][j-1] - gap
            choices = [choice1,choice2,choice3]
            score[i][j] = max(choices)    
            
            # update traceback matrix 0-diagonal, 1-up, 2-left
            traceback[i][j] = choices.index(max(choices))


# deducing the alignment from the traceback matrix
def alignment(traceback,rows,cols,seq1,seq2):

    aseq1 = ''
    aseq2 = ''
    #number of aligned movies
    count_aligned = 0
    #recommendations to be made
    recommended = []
    
    #We reconstruct the alignment into aseq1 and aseq2, 
    j = cols-1
    i = rows-1
    while i>0 and j>0:
        
        # going diagonal
        if traceback[i][j] == 0:
            aseq1 = seq1[j-1][1] + aseq1
            aseq2 = seq2[i-1][1] + aseq2
            i -= 1
            j -= 1
            count_aligned = count_aligned + 1;
            
        # going up -gap in sequence1 (top one)
        elif traceback[i][j] == 1:
            aseq1 = '_' + aseq1
            aseq2 = seq2[i-1][1] + aseq2
            #recommended movies only if rating bigger than 3
            if(float(seq2[i-1][0])==5):
                recommended.append(seq2[i-1][1])
            i -= 1
                
        # going left -gap in sequence2 (left one)
        elif traceback[i][j] == 2:
            aseq1 = seq1[j-1][1] + aseq1
            aseq2 = '_' + aseq2
            j -= 1
        else:
            #should never get here..
            print('ERROR')
            i=0
            j=0
            aseq1='ERROR';aseq2='ERROR';seq1='ERROR';seq2='ERROR'
    
    while i>0:
        #If we hit j==0 before i==0 we keep going in i (up).
        aseq1 = '_' + aseq1
        aseq2 = seq2[i-1][1] + aseq2
        #recommended movies only if rating bigger than 3
        if(float(seq2[i-1][0])==5):
            recommended.append(seq2[i-1][1])
        i -= 1     

    while j>0:
        #If we hit i==0 before j==0 we keep going in j (left).
        aseq1 = seq1[j-1][1] + aseq1
        aseq2 = '_' + aseq2
        j -= 1
        
        
    aligned = [aseq1, aseq2, count_aligned,recommended]
    
    return aligned
    
# main recommedation engine algorithm
def recommendation_engine(userId,dicio):
    
    #results = []
    #recommended_movies = []
    recommendations =[]
    lim = 0
    
    #split sequence of userId aligned i.e split ratings and movies
    aux1 = dicio[userId].split(",")
    seq1 = []
    for seq in aux1:
        seq1.append(seq.split("."))
    cols=len(seq1)+1
    
    #sort the keys, compare with users that have more reviews first
    sorted_keys = sorted(dicio, key=lambda k: len(dicio[k]), reverse=True)        
    for keys in sorted_keys:
        #condition to not align with userId 
        if(keys != userId):
            aux2 = dicio[keys].split(",")
            #condition to not perform alignments with users with only 1 movie reviewed.
            if(len(aux2)>1):
                #split sequence of all other users to be aligned i.e split ratings and movies
                seq2 = []
                for seq in aux2:
                    seq2.append(seq.split("."))
                rows=len(seq2)+1
            
                score = score_initialisation(rows,cols)
                traceback = traceback_initialisation(rows,cols)
                calculate_scores(score,traceback,rows,cols,seq1,seq2)
                
                #only perform traceback if score is different than 0, i.e an alignment was obtained
                if(score[rows-1,cols-1] != 0):
                    sequences_aligned = alignment(traceback,rows,cols,seq1,seq2)
                    s = score[rows-1,cols-1]/sequences_aligned[2]
                    
                    #only recommend movies if userId had the same opion as some other user
                    #if condition is valid then recommend movies of user2 rated as 5 that aligned with gaps of userId
                    if(s==1):
                        
                        #condition to only get 40 movies    
                        lim = lim + len(set(sequences_aligned[3]))
                        if(lim>40):
                            e = 40-len(recommendations)
                            recommendations = list(set(recommendations+sequences_aligned[3][0:e]))
                            break
                        else:
                            recommendations = list(set(recommendations+sequences_aligned[3]))

                        #used for debugging
                        #recommended_movies.append(sequences_aligned[3])
                        #aligned = []
                        #aligned.append(userId)
                        #aligned.append(aux1)
                        #aligned.append(keys)
                        #aligned.append(aux2)
                        #aligned.append(sequences_aligned[0])
                        #aligned.append(sequences_aligned[1])
                        #aligned.append(s)
                        #results.append(aligned)
                        
    return recommendations

if __name__ == '__main__':
    
    N = 1000000*9-1
    print('Preprocessing...')
    sequences = preprocessing(N)
    print('Done')
    
    while True:
        choice = input('Press 0 to exit or 1 to enter an userId\n')
        if(choice == '0'):
            break
        if(choice == '1'):
            userId = input('Enter an userID:\n')
            print('Recommended movies:\n')
            recommendations = recommendation_engine(userId,sequences)
            print(recommendations)