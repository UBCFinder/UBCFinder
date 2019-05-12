DroidPolicy is an tool that adapts text mining and NLP techniques to identify undesired behaviors from user comments and classify them into different categories summarized from the policies. 
More specifically, DroidPolicy first extracts semantic rules from a training dataset of negative user comments using a semi-automatic process, 
and then uses the extracted semantic rules to automatically identify the undesired behaviors reflected in a given comment.

1、code
(1)droidpolicy_chi.py: code of DroidPolicy for Chinese comment;
(2)droidpolicy_eng.py: code of DroidPolicy for English comment;

Usage: You need to install sysnonyms (https://github.com/huyingxi/Synonyms) and related libraries before using it.

pip install -U synonyms
pip install numpy
pip install jieba


2、Result File.

(1)malware.xlsx: comments considering undesired behaviors in malware samples.
(2)benign_chi.xlsx: comments considering undesired behaviors in Chinese benign apps.
(3)benign_eng.xlsx: comments considering undesired behaviors in Google Play benign apps.

column1: package name;
column2: undesired behaviors;
column3: comment;
column4: upload time of comment;
column5: score of comment in app market;
column6: app market;
