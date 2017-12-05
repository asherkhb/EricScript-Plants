import argparse
import os

# Parse command line arguments.
parser = argparse.ArgumentParser()
parser.add_argument("-f", "--file", help="Input SRA RunInfo Table", required=True)
parser.add_argument("-r", "--refid", help="Species refid", required=True)
parser.add_argument("-o", "--output", help="Output filename", default="config.cfg")
args = parser.parse_args()

if not os.path.isfile(args.file):
    print("Error: Specified SRA RunInfo Table doesn't exist.")
    exit(1)
if os.path.isfile(args.output):
    print("Error: Output file %s already exists. Please (re)move or specify an alternate name using -o.")
    exit(1)

# Convert SRA RunInfo Table to Pipeline CFG.
with open(args.file, 'r') as inp, open(args.output, 'w', 1) as otp:
    # Deal with input header.
    h = inp.readline().strip().split("\t")
    srr_idx = h.index("Run_s")
    
    # Deal with output header.
    otp.write("sample_name,refid,sra\n")

    # Write entry for each run.
    for line in inp.readlines():
        line = line.strip().split("\t")
        try:
            srr = line[srr_idx]
            otp.write("%s,%s,%s\n" % (srr, args.refid, srr))
        except IndexError:
            print("Warning: line missing accession ID (%s)" % '\t'.join(line))

# Print concluding message.
print("Complete! Output written to %s." % args.output)