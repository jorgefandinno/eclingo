import argparse
import subprocess
import os
import re
import pandas as pd
import pathlib

def get_time_value(cmd):

    result = subprocess.check_output(cmd,shell=True).decode('utf-8')
    lines = result.splitlines()

    find1 = result.find('SATISFIABLE')
    find2 = result.find('UNSATISFIABLE')

    # print(result)
    if(find2!=-1 or find1==-1):
        print("error in file")
        exit(0)
    
    # print(result)

    if(args.cputime):
        filtered = filter(lambda x: x.find("#   total CPU time (s): ")!=-1, lines)
        time = "CPU TIME"
        val = list(filtered)[0].split(" ")[-1]
    
    else:
        filtered = filter(lambda x: x.find("#   total CPU user time (s): ")!=-1, lines)
        time_type = "USER TIME"
        val = list(filtered)[0].split(" ")[-1]

    return time_type, val



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--usertime", action="store_true", help="show user time")
    parser.add_argument("-c", "--cputime", action="store_true", help="show cpu time")
    args = parser.parse_args()

    # subprocess.run(["./runsolver","--timestamp", "-C 1200", "-W 180", "-R 8192", "-V 102400", "-w watch.log", "-v values.log", "-o tool_output.log","python /home/ubuntu/asp/old/eclingo/eclingo/main.py", "-c length=9 0 /home/ubuntu/asp/old/eclingo/test/yale/yale.lp /home/ubuntu/asp/old/eclingo/test/yale/input/yale01.lp"])
    # os.system("./runsolver --timestamp -w newclingo_watch2.log -v newclingo_values2.log -o newclingo_tool_output2.log python eclingo/eclingo/main.py -c length=9 0 eclingo/test/yale/yale.lp eclingo/test/yale/input/yale02.lp")
    
    
    commands = ["./runsolver --timestamp python eclingo/main.py -c length=9 0 test/yale/yale.lp test/yale/input/yale01.lp"]

    
    # df = pd.DataFrame(test, columns=['INSTANCE', 'TIME', 'TIME_TYPE'])
    # print(test)

    folders=['eligible', 'yale']

    test_path = "test/"
    commands=[]

    for folder in folders:
        path = pathlib.Path().resolve()

        print(path)
        

    results=[]
    for cmd in commands:
        time_type, val = get_time_value(cmd)

        results.append(['instance',val,time_type])

    print(results)









# ./runsolver --timestamp -C 1200 -W 180 -R 8192 -V 102400 -w watch.log -v values.log -o tool_output.log python eclingo/eclingo/main.py -c length=9 0 eclingo/test/yale/yale.lp eclingo/test/yale/input/yale01.lp