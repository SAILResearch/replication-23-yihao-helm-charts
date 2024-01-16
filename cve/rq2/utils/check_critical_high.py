string1 = '1;2;6;8;9;11;12;13;14;16;23;29;31;32;37;46;50;51;61;64;69;70;72;73;78;79;82;88;94'

string2 = '3;10;11;12;22;23;24;25;26;28;29;31;36;37;50;56;60;61;64;67;69;70;74;83;84;86;87;94'


# join
def join_str(string1, string2):
    combined = string1.split(';') + string2.split(';')
    return combined


notin = []
joined = join_str(string1, string2)

for i in range(1,91):
    if str(i) not in joined:
        notin.append(i)
print(notin)
print(len(notin))