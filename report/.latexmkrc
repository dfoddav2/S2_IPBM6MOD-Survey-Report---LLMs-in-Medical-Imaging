$pdf_mode = 1;
$pdflatex = 'pdflatex -interaction=nonstopmode %O %S';
$bibtex = 'bibtex %O %B';
$bibtex_format = 'bibtex8';
$makeindex = 'makeindex %O %O -o %D %S';
$clean_ext .= ' %R-blx.bib';

# Set the command for bibtex
system("bibtex report");