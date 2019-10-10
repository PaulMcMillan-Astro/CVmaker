
import os
import sys 
from pylatexenc.latexencode import unicode_to_latex
import ads
import subprocess


FullName = 'Paul McMillan'
Surname = 'McMillan'
filename = Surname + '_PublicationList.tex'


def AuthorNameAbbreviation(author) :
    '''Give author name in LaTeX with format: Surname, FirstInitial.'''
    # Convert to Latex
    fullname = unicode_to_latex(author)
    # Replace first names with first initial
    commaplace = fullname.find(',')
    if commaplace >=0 :
        if(fullname[:commaplace] == Surname) :
            return '\\textbf{'+ fullname[:commaplace+3] +'.}'
        else :
            return fullname[:commaplace+3] + '.'
    else :
        return fullname
        

def JournalVolumePage(article) :
    '''Give journal, volume, page as string (coping with arXiv or in press)'''
    if unicode_to_latex(article.bibstem[0]) == 'arXiv' :
        return article.page[0]
    elif article.volume is None :
        return  unicode_to_latex(article.bibstem[0])+', in press'
    else :
        return unicode_to_latex(article.bibstem[0])+', ' + str(article.volume) \
            +', ' + article.page[0]



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

# Text that comes before publication list
Header = "\\documentclass{resume}\n" + \
    "\\usepackage[left=0.75in,top=0.8in,right=0.75in,bottom=1in]{geometry} \n" + \
    "\\name{\\vspace{-1.5mm}Publication List - Paul McMillan}\n" +\
    "\\address{Lund Observatory \\\\ paul@astro.lu.se}\n" +\
    "\\address{%d total citations \\\\ " % Ncites 
Header +=  "%d citations as first author }" % NcitesFirstAuthor

Header += "\n\n\n\\begin{document}\n\n\\begin{enumerate}\n"

# end text
Footer = "\\end{enumerate}\n\n\\end{document}\n"


fileout = open(filename,'w')

fileout.write(Header)

for article in articles :
    # enumerated list
    fileout.write ('\\item ``' + unicode_to_latex(article.title[0])+'\'\', ')
    # Solo papers
    if len(article.author) ==1 :
        fileout.write ( AuthorNameAbbreviation(article.author[0]) + ' ')
    # Short author lists
    elif len(article.author) <=4 :
        for i in range(len(article.author)-1) :
            fileout.write ( AuthorNameAbbreviation(article.author[i]) )
            if (i<len(article.author)-2): fileout.write(', ')
        fileout.write(' \\& ' +
                      AuthorNameAbbreviation(article.author[len(article.author)-1]) +' ')
    else :
    # Long author lists
        for i in range(4) :
            fileout.write(AuthorNameAbbreviation(article.author[i]) +', ')
        fileout.write ('et al. ')

    fileout.write ('('+ article.year + '), ' + JournalVolumePage(article) + '.')
    # Citations?
    if article.citation_count > 0 :
        fileout.write (' (Citations to date ' + str(article.citation_count) +'.)\n\n')
    else :
        fileout.write ('\n\n')
fileout.write(Footer)
fileout.close()

# Convert to pdf
subprocess.call(["pdflatex", filename])