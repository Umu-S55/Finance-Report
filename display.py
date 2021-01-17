#! python3
# csv_graph.py - EPS/Revenueを取得するスクリプト

import csv
import re
import os
import pandas as pd
import matplotlib.pyplot as plt
%matplotlib inline


if __name__ == '__main__':
    files = os.listdir()
    csv_files = []
    for i in files:
        if 'csv' in i:
            csv_files.append(i)
        
    for i in csv_files:
        cname = i[15:].rstrip(name[-4:])
        data = pd.read_csv(i,sep='\t')
        data = data.sort_values(by='Unnamed: 0', ascending=False)
        
        fig = plt.figure(figsize=(20.0,4.0))
        ax1 = fig.add_subplot(1,2,1)
        ax2 = fig.add_subplot(1,2,2)
        ax1.plot(data['Period'], data['EPS(Surprise)'], label=cname)
        ax1.axhline(y=0, color='k', alpha=0.3, linestyle='dashed')
        ax1.set_xticklabels(data['Period'],rotation=45)
        ax1.legend()
        
        ax2.plot(data['Period'], data['Revenue(Surprise)'], label=cname)
        ax2.axhline(y=0, color='k', alpha=0.3, linestyle='dashed')
        ax2.set_xticklabels(data['Period'],rotation=45)
        ax2.legend()