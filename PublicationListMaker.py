
import os
import sys 
from pylatexenc.latexencode import unicode_to_latex
import ads
import subprocess


FullName = 'Paul McMillan'
Surname = 'McMillan'
# My ORCID. Replace with your own if you so desire
ORCID = '0000-0002-8861-2620'

AuthorName = '\\textbf{Paul McMillan}'
filename = Surname + '_PublicationList.tex'
separateKeyPublications = True
additionalPreprints = False

KeyPublications = [ '2020AJ....160...83S', # 'The Sixth Data Release of the Radial Velocity Experiment (RAVE) -- II: Stellar Atmospheric Parameters, Chemical Abundances and Distances',
                    '2019MNRAS.487.3568S', # 'Distances and parallax bias in Gaia DR2',
                    '2018A&A...616A..12G', #'Gaia Data Release 2. Kinematics of globular clusters and dwarf galaxies around the Milky Way',
                    '2018MNRAS.477.5279M', #'Improved distances and ages for stars common to TGAS and RAVE',
                    '2017MNRAS.467.1154S', #'Understanding inverse metallicity gradients in galactic discs as a consequence of inside-out formation'
                    '2017MNRAS.465...76M', #'The mass distribution and gravitational potential of the Milky Way',
                    '2017AJ....153...75K', #'The Radial Velocity Experiment (RAVE): Fifth Data Release',
                    '2016MNRAS.456.1982B', #'Torus mapper: a code for dynamical models of galaxies',
                    '2014MNRAS.445.3133P', #"Constraining the Galaxy's dark halo with RAVE stars",
                    '2013MNRAS.433.1411M', #'Analysing surveys of our Galaxy - II. Determining the potential',
                    '2013MNRAS.430.3276M', #'Extending the Hyades',
                    '2011MNRAS.414.2446M', #'Mass models of the Milky Way',
                    '2011MNRAS.413.1889B', #'Models of our Galaxy - II',
                    '2010MNRAS.402..934M', #'The uncertainty in Galactic parameters',
                    '2008MNRAS.390..429M', #'Disassembling the Galaxy with angle-action coordinates',
                    '2007MNRAS.378..541M', #'Initial conditions for disc galaxies',
                    '2005MNRAS.363.1205M'] #'Halo evolution in the presence of a disc bar'
nArticlesMax = 2000


def SurnameofListmaker(author) :
    '''Boolian. True if author is the one we're making the list for.'''
    fullname = unicode_to_latex(author)
    return (fullname[:len(Surname)] == Surname)

def AuthorNameAbbreviation(author) :
    '''Give author name in LaTeX with format: Surname, FirstInitial.'''
    # Convert to Latex
    fullname = unicode_to_latex(author)
    # Replace first names with first initial
    commaplace = fullname.find(',')
    if commaplace >=0 :
        if(fullname[:commaplace] == Surname) :
            return AuthorName
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

def WriteArticleListing(fileout,article) :
    '''Writes latex ebtry for paper in my preferred format'''
    SurnameFound = False
    # latex for enumerated list
    fileout.write ('\\item ``' + unicode_to_latex(article.title[0])+'\'\', ')
    # Solo papers
    if len(article.author) ==1 :
        fileout.write ( AuthorNameAbbreviation(article.author[0]) + ', ')
    # Short (N<4) author lists
    elif len(article.author) <=4 :
        for i in range(len(article.author)-1) :
            fileout.write ( AuthorNameAbbreviation(article.author[i]) )
            if (i<len(article.author)-2): fileout.write(', ')
        fileout.write(' \\& ' +
                      AuthorNameAbbreviation(article.author[len(article.author)-1]) +', ')
    else :
    # Long author lists
        for i in range(4) :
            fileout.write(AuthorNameAbbreviation(article.author[i]) +', ')
            if SurnameofListmaker(article.author[i]) : SurnameFound = True
        if SurnameFound :
            fileout.write ('et al., ')
        else :
            fileout.write ('et al. (including ' + AuthorName + '), ')

    fileout.write (article.year + ', ' + JournalVolumePage(article) + '.')
    # Citations?
    if (article.citation_count is None) or (article.citation_count == 0) :
        fileout.write ('\n\n')
    else :
        fileout.write (' \\textit{(Citations to date ' + str(article.citation_count) +')}\n\n')
    






articles = list(ads.SearchQuery(
        q='(orcid:'+ ORCID +')'\
          'database:astronomy',rows=nArticlesMax,
        fl=['id', 'first_author','author', 
            'author_norm', 'year', 'title','citation_count', 'volume','bibstem',
            'page','identifier','bibcode'],
        sort='date'))

if (len(articles) == nArticlesMax) :
    print('WARNING: Too many articles to parse')

# Remove articles I don't really want in there
for i,article in enumerate(articles) :
    Journal = unicode_to_latex(article.bibstem[0])
    if ( Journal == 'EAS') | (Journal == 'EPJWC') : 
        del articles[i]

        
# Count citations
Ncites = 0
NcitesFirstAuthor = 0
print('bibcodes are:')
for article in articles :
    print(article.title[0],article.bibcode)
    if article.citation_count is not None :
        Ncites += article.citation_count
        if article.first_author[0:len(Surname)] == Surname : 
            NcitesFirstAuthor += article.citation_count

print()

# Text that comes before publication list
Header = "\\documentclass{resume}\n" + \
    "\\usepackage[left=0.75in,top=0.8in,right=0.75in,bottom=1in]{geometry} \n" + \
    "\\name{\\vspace{-1.5mm}Publication List - " + FullName + "}\n" +\
    "\\address{Lund Observatory \\\\ paul@astro.lu.se}\n" +\
    "\\address{%d total citations \\\\ " % Ncites 
Header +=  "%d citations as first author }" % NcitesFirstAuthor

if separateKeyPublications is True :
    Header += "\n\n\n\\begin{document}\n\n\\section*{Key Publications}\n\n" \
            + "\\begin{enumerate}\n"
else :
    Header += "\n\n\n\\begin{document}\n\n\\begin{enumerate}\n"


# end text
Footer = "\\end{enumerate}\n\n\\end{document}\n"


fileout = open(filename,'w')

fileout.write(Header)

numberofAdditionalKeyPreprints = 0
if additionalPreprints is True :
    # Add as many as you like - this is mine
    fileout.write('\\item ``Example Paper\'\', Authors et al. including \\textbf{Paul McMillan}, '
    + ' 2020, AJ, submitted (arXiv:XXX).\n' )
    numberofAdditionalKeyPreprints += 1

if separateKeyPublications is True :
    for i,article in enumerate(articles) :
        if article.bibcode in KeyPublications :
            # write article to file
            WriteArticleListing(fileout,article)
    KeyPublicationNumber = len(KeyPublications)
    if additionalPreprints is True : KeyPublicationNumber += numberofAdditionalKeyPreprints
    fileout.write("\\end{enumerate}\\section*{Other Publications}\n\n"
                  + "\\begin{enumerate}\n\\setcounter{enumi}{%d}\n" % KeyPublicationNumber)

if additionalPreprints is True :
    fileout.write('\\item other item \n')
for article in articles :
    if (separateKeyPublications is False) or (article.bibcode not in KeyPublications) :
        WriteArticleListing(fileout,article)

fileout.write(Footer)
fileout.close()

# Convert to pdf
subprocess.call(["pdflatex", filename])