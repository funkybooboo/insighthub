.PHONY: all clean

OUTPUT = nate_stott_project_2_cs6600_report.pdf
SOURCE = report.md

all: $(OUTPUT)

$(OUTPUT): $(SOURCE)
	pandoc $(SOURCE) -o $(OUTPUT) \
		--pdf-engine=xelatex \
		--variable geometry:margin=1in \
		--variable fontsize=12pt \
		--toc \
		--number-sections

clean:
	rm -f $(OUTPUT)
