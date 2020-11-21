CHAMP(UBCFinder) is an tool that adapts text mining and NLP techniques to identify undesired behavior comments and classify them based on market policies. 
More specifically, UBCFinder first extracts semantic rules from a manual labelled training dataset of user comments automatically, 
and then uses the extracted semantic rules to automatically identify the undesired behaviors reflected in a given comment.

1、UBCFinder_chi.py and UBCFinder_eng.py are scripts for identifying Chinese UBComments and English UBComments repectively.

Usage: You need to install sysnonyms (https://github.com/huyingxi/Synonyms) and related libraries before using it.

pip install -U synonyms

pip install numpy

pip install jieba

You can extract undesired behavior comments by directly invoking the method detect('your comment here')

2、Market_policy.pdf contains the market policies we collected from Google Play and 8 Chinese thrid-party markets.

3、The file "labelled comments.xlsx" contains UBComments tagged by manual inspection.

4、The identified UBComments are shown in "malware.xlsx"、"benign&gray_chi.xlsx" and "benign&gray_eng.xlsx".

column1: package name;

column2: undesired behaviors;

column3: comment;

column4: upload time of comment;

column5: score of comment in app market;

column6: app market;

column7: number of anti-malware engines which have flagged the app;
