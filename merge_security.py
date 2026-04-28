import os

with open('security/Interview.md', 'w') as f:
    f.write('# Interview QnA: Security & Obfuscation\n\n')
    
    f.write('## Part 1: General Security\n\n')
    with open('testing/interview.md', 'r') as tf:
        lines = tf.readlines()
        in_sec = False
        for line in lines:
            if '## Security Interview Questions' in line:
                in_sec = True
                continue
            if in_sec:
                f.write(line)
                
    f.write('\n## Part 2: Permissions & Components\n\n')
    with open('security/Permissions.md', 'r') as p: # Wait, the interview file was android-manifest/Interview.md
        pass # I'll read it from memory since I deleted the folder? No I haven't deleted the folder yet!
