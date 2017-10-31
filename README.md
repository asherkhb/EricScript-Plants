# EricScript, but for Plants

A modified version of [EricScript](https://sites.google.com/site/bioericscript/) which works with the EnsemblPlants database. Provided as a Dockerfile for easy use.

## About

To simplify using the program, a Dockerfile is provided which will create a Docker image suitable for running the full pipeline. This README covers the use of the Docker version of the tool. 
If you are interested in "normal" system installation, or the modified EricScript code, you should see EricScript-Plants/README.md.

All credit for EricScript goes to the original writer Matteo Benelli. See his version [here](https://sites.google.com/site/bioericscript/), and cite him 
[appropriately](https://www.ncbi.nlm.nih.gov/pubmed/23093608)

> Benelli M, Pescucci C, Marseglia G, Severgnini M, Torricelli F, Magi A. **Discovering chimeric transcripts in paired-end RNA-seq data by using EricScript.** Bioinformatics. 2012; 28(24): 3232-3239.

## Using the EricScript Plants Docker Container

This section assumes you have a working Docker installation, and have the necessary permissions set to use Docker without sudo. Docker installation is out-of-scope here, but complete instructions 
for most platforms can be found at the [official Docker documentation](https://docs.docker.com/).

### Obtaining the Docker Image

These instructions are specific for Mac & Linux. Windows users will follow a similar pattern, but may need to make system-specific modifications.

#### Method 1: Build from Dockerfile

```
[~]$ git clone https://github.com/asherkhb/EricScript-Plants
[~]$ cd EricScript-Plants
[~/EricScript-Plants]$ docker build --rm -t EricScriptPlants .
...
[~/EricScript-Plants]$ docker images
REPOSITORY                   TAG                 IMAGE ID            CREATED             SIZE
EricScriptPlants             latest              2ceaf70cd914        19 minutes ago      956MB
...
```

#### Method 2: Pull from Docker Hub

```
[~]$ docker pull asherkhb/EricScriptPlants:latest
```

### Using the Docker Image

#### Method 1: Create interactive containers (preferred)

The general workflow of this method is to create an interactive container which you can then work with to execute analyses. Personally, I prefer this workflow as it is simpler for me. 

*Note that you need to replace those arguments contained in `<these arrow brackets>` with an appropriate value for your system/analysis*

Launch...
```
[~]$ docker run --name <interactive_esp> -itd -v </abs/path/to/storage>:/usr/local/data EricScriptPlants:latest
...
```

The previous command launches an interactive bash session in a Docker container, then detaches. You can attach to this bash session (PID 1) using `docker attach <interactive_esp>`. 
Detach from an attached interactive (-it) session using Ctrl-p, Ctrl-q (Ctrl-p, then q still holding down ctrl). You can only reattach to PID 1, so plan accordingly.

Start an analysis step...
```
[~]$ docker exec -it <interactive_esp> bash
root@hash:/usr/local/data# <analysis_command> 2>&1 <logfile.txt>
{Detach: Ctrl-P, Ctrl-Q}
```

Here, you are launching an analysis step and redirecting all output to a logfile. I prefer logging to a file on the mounted volume so I can inspect progress without using special Docker commands.
If you prefer to an alternative, such as checking using `docker logs`, you can omit the `2>&1 <logfile.txt>` portion.

An (incomplete) list of most commonly used commands...
* Download FASTQ files from SRA: `fastq-dump --split-files <SRR>`
* List available species: `ericscript --printdb`
* Build a reference for species: `ericscript --downdb --refid <refid> -db References`
* Find chimeric transcripts: `ericscript -p <cores> -db <References_folder> --refid <refid> -name <analysis_name> -o <output_folder> <R1_1.fq> <R2_2.fq>`


#### Method 2: Create detached, single-process containeres.

You can also launch containers that execute a command directly without interactive nature. I don't prefer this method (as of now), but it can be useful in some situations.

```
[~]$ docker run --name <analysis_ex> -d -v </abs/path/to/storage>:/usr/local/data EricScriptPlants:latest "<command>"
```

For command ideas, see the list in Method 1. Note that the full command will need to be quoted.