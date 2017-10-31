# EricScript-Plants
A custom modified version of EricScript (https://sites.google.com/site/bioericscript/) designed to work with EnsemblPlants.

## About
* EricScript is a software package developed in R, perl and bash scripts.
* EricScript (original) was developed by: matteo.benelli AT gmail.com.
* This version was modified by asherkhb [ahaug AT email DOT arizona DOT edu] to work with the EnsemblPlants database.
* EricScript uses the BWA aligner to perform the mapping on the transcriptome reference and samtools to handle with
SAM/BAM files. Recalibration of the exon junction reference is performed by using BLAT.


## Requirements/Dependencies (must be downloaded, installed, and included in your $PATH)
* R: http://cran.r-project.org/
  * "ada" R package: http://cran.r-project.org/web/packages/ada/index.html
* BWA: http://bio-bwa.sourceforge.net
* SAMtools (>0.1.17): http://samtools.sourceforge.net/
* bedtools (>2.15): http://code.google.com/p/bedtools/
* BLAT: http://genome-test.cse.ucsc.edu/~kent/exe/
* seqtk: https://github.com/lh3/seqtk



## Usage
### Before running for the first time, you need to make ericscript.pl executable:
```
chmod +x /PATH/TO/ERIC/ericscript.pl
```

### To make it even easier, create a symlink in your path:
```
INSTRUCTIONS
```

### To get information about running EricScript:
```
ericscript --help
```

### List available Ensembl Databases:
```
ericscript --printdb
```

### Download & build a database.
#### Download latest release.
```
ericscript --downdb --refid <REFID> -db </PATH/TO/DBFOLDER>
```
#### Select a specific release. NOTE: This is untested!
```
ericscript --downdb --refid <REFID> -db </PATH/TO/DBFOLDER> --ensversion <VERSION>
```

### Check if databases are up-to-date:
```
/PATH/TO/ERIC/ericscript.pl --checkdb
```

### Run EricScript with default parameters:
```
ericscript -db </PATH/TO/DBFOLDER> --refid <REFID> -name <SAMPLENAME> -o </PATH/TO/OUTPUT/> <R1.FQ> <R2.FQ>
```


## Output Files (/PATH/TO/OUTPUT/)
* samplename.results.total.csv: contains all the predicted gene fusions.
* samplename.results.filtered.csv: contains the predicted gene fusions with EricScore > 0.50.