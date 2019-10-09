
import os
import sys 
from pylatexenc.latexencode import unicode_to_latex
import ads
import subprocess




FullName = 'Paul McMillan'
Surname = 'McMillan'

# My ORCID. Replace with your own if you so desire
ORCID = '0000-0002-8861-2620'


articles = list(ads.SearchQuery(
        q='(orcid:'+ ORCID +')'\
          'database:astronomy',rows=200,
        fl=['id', 'first_author','author', 
            'author_norm', 'year', 'title','citation_count', 'volume','bibstem',
            'page','identifier'],
        sort='date'))


# Remove articles I don't really want in there
for i,article in enumerate(articles) :
    Journal = unicode_to_latex(article.bibstem[0])
    if ( Journal == 'EAS') | (Journal == 'EPJWC') : 
        del articles[i]

        
# Count citations
Ncites = 0
NcitesFirstAuthor = 0
for article in articles :
    Ncites += article.citation_count
    if article.first_author[0:len(Surname)] == Surname : 
        NcitesFirstAuthor += article.citation_count


Header = "\\documentclass{resume}\n" + \
    "\\usepackage[left=0.75in,top=0.8in,right=0.75in,bottom=1in]{geometry} \n" + \
    "\\name{\\vspace{-1.5mm}Publication List - Paul McMillan}\n" +\
    "\\address{Lund Observatory \\\\ paul@astro.lu.se}\n" +\
    "\\address{%d total citations \\\\ " % Ncites 
Header +=  "%d citations as first author }" % NcitesFirstAuthor

Header += "\n\n\n\\begin{document}\n\n\\begin{enumerate}\n"
Footer = "\\end{enumerate}\n\n\\end{document}\n"

filename = Surname + '_PublicationList.tex'

fileout = open(filename,'w')

fileout.write(Header)

for article in articles :
    fileout.write ('\\item ``' + unicode_to_latex(article.title[0])+'\'\', ')
    if len(article.author) ==1 :
        fileout.write ( unicode_to_latex(article.author_norm[0]) + '. ')
    elif len(article.author) <=4 :
        for i in range(len(article.author)-1) :
            fileout.write ( unicode_to_latex(article.author_norm[i]) +'.')
            if (i<len(article.author)-2): fileout.write(', ')
        fileout.write(' \\& ' +
                      unicode_to_latex(article.author_norm[len(article.author)-1]) +'. ')
    else :
        for i in range(4) :
            fileout.write(unicode_to_latex(article.author_norm[i]) +'., ')
        fileout.write ('et al. ')
    fileout.write ('('+ article.year + '), ' + \
            unicode_to_latex(article.bibstem[0])+', ' + str(article.volume) \
            +', ' + article.page[0] +'. (Citations to date ' + str(article.citation_count) +')\n\n')
 
fileout.write(Footer)


fileout.close()

subprocess.call(["pdflatex", filename])