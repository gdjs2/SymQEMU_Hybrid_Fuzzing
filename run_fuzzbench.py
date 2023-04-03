import subprocess
import sys
import time
import os
import shutil

FUZZING_HELPER = '/src/symcc/util/symcc_fuzzing_helper/target/release/symcc_fuzzing_helper'
SYMQEMU = '/src/symqemu/build/x86_64-linux-user/symqemu-x86_64'
BIN_DIR = '/workdir/bench/evaluation_binaries/build-programs'
SEED_DIR = '/workdir/seeds/real_seeds'
CORPUS_DIR = '/workdir/corpus'
SECONDARY_Q_DIR = '/workdir/afl_out/afl-secondary/queue'
STATS_FILE = '/workdir/afl_out/afl-secondary/fuzzer_stats'
STATS_PATTERN = 'command_line      : /src/AFLplusplus/afl-fuzz -Q -S afl-secondary -i corpus -o afl_out -m none -- {} @@'
AFL_OUT_DIR = '/workdir/afl_out'
OUTPUT_DIR = '/tmp/output'
COUNT = 1


def prepare(target):
	if os.path.exists(AFL_OUT_DIR): # afl_out
		shutil.rmtree(AFL_OUT_DIR)
	if os.path.exists(CORPUS_DIR): # corpus
		shutil.rmtree(CORPUS_DIR)
	if os.path.exists(OUTPUT_DIR): # /tmp/output
		shutil.rmtree(OUTPUT_DIR)

	os.makedirs(CORPUS_DIR)
	os.makedirs(SECONDARY_Q_DIR)
	os.makedirs(OUTPUT_DIR)
	
	stats = open(STATS_FILE, 'w')
	stats.write(STATS_PATTERN.format(os.path.join(BIN_DIR, target+'.native')))
	stats.close()

	seeds_dir = os.path.join(SEED_DIR, target+'_reduced')
	seeds_files = os.listdir(seeds_dir)
	for file in seeds_files:
		shutil.copy(os.path.join(seeds_dir, file), SECONDARY_Q_DIR)


def run(target):
	start_time = time.time()
	subprocess.run([FUZZING_HELPER, '-o', 'afl_out', '-a', 'afl-secondary', '-n', 'symqemu', '--', SYMQEMU, os.path.join(BIN_DIR, target+'.native'), '@@'])
	print('{} running time: {}'.format(target, time.time() - start_time))

if __name__ == '__main__':
	target = sys.argv[1]

	if (target == 'all'):
		prgs = os.listdir(BIN_DIR)
		for prg in prgs:
			target = prg.split('.')[0]
			# print(target)
			prepare(target)
			run(target)
	else:
		prepare(target)
		run(target)