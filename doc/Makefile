

sonata.1:
	/usr/bin/xsltproc --nonet --param make.year.ranges 1 --param make.single.year.ranges 1 \
		--param man.charmap.use.subset 0 \
		/usr/share/xml/docbook/stylesheet/docbook-xsl-ns/manpages/docbook.xsl \
		sonata.1.xml

sonata.1.html:
	/usr/bin/xsltproc /usr/share/xml/docbook/stylesheet/docbook-xsl-ns/html/docbook.xsl sonata.1.xml > ./sonata.1.html

man: sonata.1

html: sonata.1.html

pdf: man
	/usr/bin/man -l -Tps sonata.1 | /usr/bin/ps2pdf - ./sonata.1.pdf

all: man html pdf

clean:
	rm -rf sonata.1.pdf sonata.1.html sonata.1
