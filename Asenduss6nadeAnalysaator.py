import re

paths = ["C:\\Users\\linda96\\Documents\\anafoorikorpus\\anafoorikorpus\\tea_eesti_arst_2004.anaf",
"C:\\Users\\linda96\\Documents\\anafoorikorpus\\anafoorikorpus\\aja_EPL_2007_08_12.tasak.anaf",
"C:\\Users\\linda96\\Documents\\anafoorikorpus\\anafoorikorpus\\aja_ml_2002_47.tasak.anaf",
"C:\\Users\\linda96\\Documents\\anafoorikorpus\\anafoorikorpus\\aja_pm_1998_09_26e.tasak.anaf",
"C:\\Users\\linda96\\Documents\\anafoorikorpus\\anafoorikorpus\\aja_ee_1999_20.tasak.anaf"]

pronoomenid = ['mina', 'sina', 'tema', 'see', 'kes','mis']

#Info goes into that 'material' dictionary in the end
material = {'mina': [], 'sina': [], 'tema': [], 'see': [], 'kes': [],
                'mis': [], "mis_sugune": [], 'mitmes': [], 'selline': []}

for path in paths:
    #Read files via lines into list.
    sonadeArvLauses = [] #List, kus on iga lause sõnade arv.
    file = open(path, encoding="utf8")
    data = file.readlines()
    data = [x.strip() for x in data]
    file.close()

    #Adding sentence numbers in the end of each line.
    sentenceNr = 0
    index = 0
    for line in data:
        m = re.search('\"<s id=\"([0-9]+)\">\"', line)
        if m:
            sentenceNr = m.group(1)
        data[index] = line + " STNR" + str(sentenceNr)
        index += 1

    # Adding amount of words in a sentence to the end of a line.
    # Koos punktiga nagu failis on(!). Ka punkt on arvestatud lause pikkusesse.
    lastWord = ""
    amountOfWords = 0
    sentenceEndIndex = 0
    sentenceStartIndex = 0
    for index, line in enumerate(data):
        if re.match('\"<s id=\"[0-9]+\">\"', line):
            sentenceStartIndex = index
        if re.match('\"</s>\"', line):
            lastWord = data[index-1]
            sentenceEndIndex = index - 1
            m = re.search('#([0-9]+)->[0-9]+', lastWord)
            if m:
                amountOfWords = m.group(1)
                sonadeArvLauses.append(amountOfWords)
        while (sentenceEndIndex > sentenceStartIndex ):
            data[sentenceEndIndex] = data[sentenceEndIndex] + ' AOW' + str(amountOfWords)
            sentenceEndIndex -= 1

    # Add the actual wordform in the end of the line
    for index, line in enumerate(data):
        if re.match('.+{Pronoomen}', line):
            m = re.search('\"<(.+)>.+', data[index-1])
            if m:
                trueForm = m.group(1)
            data[index] = line + " SNVRM:" + trueForm
        if re.match('.+{Viitealus}', line):
            m = re.search('\"<(.+)>.+', data[index - 1])
            if m:
                trueForm = m.group(1)
            data[index] = line + " SNVRM:" + trueForm

#Get all a list containing only Viitealus and Pronoomen lines.
    info = []
    for line in data:
        if re.match('.+{Pronoomen}', line):
            info.append(line)
        if re.match('.+{Viitealus}', line):
                info.append(line)

#If pronomen has only {Viitealus} signature, add {Pronoomen} in the end.
    for index, line in enumerate(info):
        for pron in pronoomenid:
            if re.search('\"' + pron + '\"', line):
                if re.search(' P ', line):
                    if re.search('{Viitealus}', line):
                        info[index] = line + ' {Pronoomen}'

# Puts pronomen info into list:
# ['P', sõna vorm, sõnade arv lauses, lause nr, koht lauses, süntaks, arv, sõna algvorm ehk lemma, kääne,(inter rel|dem|pers|pos|det ref|det),
                    # pööre(kui on), failinimi, coref, ülemusverbi number].
# *** => Kogu see teave, mis on P-i ja arvu vahel (erineva pikkusega list).
# tavaliselt on seal pronoomeniliik ja/või teine liik või arv.
    def pronomenInfoIntoList(line):
        list = ["XXX"]*12
        list[0] = ('P')
        m = re.search('STNR([0-9]+) AOW([0-9]+) SNVRM:([^ ]+)', line)
        if m:
            list[1] = (m.group(3).lower()) #word form
            list[2] = (m.group(2)) #amount of words in sentence
            list[3] = (m.group(1)) #sentence nr.
        g = re.search('@(.+) #([0-9]+)->([0-9]+) ', line)
        if g:
            list[4] = (g.group(2)) #koht lauses
            list[5] = (g.group(1)) #süntaks
            list[11] = (g.group(3))
        r = re.match('.+ (sg|pl)', line)
        if r:
            list[6] = (r.group(1)) #sg|pl
            #list.append(r.group(2))
        o = re.match('\"([a-z].+)\"', line)
        if o:
            list[7] = (o.group(1)) #word lemma, 8th thing, list[7]
        r = re.match('.+(nom|gen|part|ill|in|el|all|ad|abl|tr|term|es|abes|kom).+', line)
        if r:
            list[8] = (r.group(1)) #kääne
        r = re.match('.+(inter rel|dem|pers|pos|det ref|det|indef|dem indef).+', line)
        if r:
            list[9] = (r.group(1))
        r = re.match('.+(ps3|ps2|ps1).+', line)
        if r:
            list[10] = (r.group(1))
        failinimeTykid = path.split("\\")
        list.append(failinimeTykid[6])
        m = re.search('{Coref:([^}]+)}', line)
        if m:
            list.append(m.group(1))
        return list
#arvutab asendussõna ja viitealuse vahelisi kaugusi. Koha 1 ja 3 vahel on 1 sõne, 1 ja 4 vahel 2 sõne jne.
    def distanceCalculator(proLauseNr, anaLauseNr, anaPositsioonLauses, proPositsioonLauses):
        if (proLauseNr == anaLauseNr):
            if (anaPositsioonLauses < proPositsioonLauses):
                kaugus = (anaPositsioonLauses + 1) - proPositsioonLauses
            if (anaPositsioonLauses > proPositsioonLauses):
                kaugus = (anaPositsioonLauses - 1) - proPositsioonLauses
            return kaugus  # kaugus on negatiivne, kui anafoor on pronoomenist eespool
        elif (proLauseNr > anaLauseNr):
            kaugus = int(proPositsioonLauses - 1)  # pronoomen ise arvestusse ei lähe ju.
            while (proLauseNr - 1 > anaLauseNr):
                kaugus = kaugus + int(sonadeArvLauses[proLauseNr - 2])
                proLauseNr -= 1
            kaugus += (int(sonadeArvLauses[anaLauseNr - 1]) - (anaPositsioonLauses))
            return (-1 * kaugus)
        else:  # (anaLauseNr > proLauseNr)
            kaugus = anaPositsioonLauses - 1
            while (anaLauseNr - 1 > proLauseNr):
                kaugus = kaugus + (int(sonadeArvLauses[anaLauseNr - 2]))
                anaLauseNr -= 1
            kaugus += int(sonadeArvLauses[proLauseNr - 1]) - proPositsioonLauses
            return abs(kaugus)

#paneb listi tunnused, mis on kõigil sõnaliikidel listis.
    def commonInfoIntoList(list, line):
        m = re.search('.+STNR([0-9]+) AOW([0-9]+) SNVRM:([^ ]+)', line)
        if m:
            list[2] = m.group(3) #sõnavorm
            list[3] = m.group(2) #sõnade arv lauses
            list[4] = m.group(1) #lause number
        g = re.search('.+@(.+) #([0-9]+)->([0-9]+) ', line)
        if g:
            list[5] = g.group(2) #koht lauses
            list[6] = g.group(1) #süntaktiline funktsioon
            list[9] = g.group(3) #ülemuse number
        r = re.match('.+ (sg|pl) .+', line)
        if r:
            list[7] = r.group(1) #mitmus v ainsus (kui on)
        return list


#Viitealuste info listi.
#Kui on S nimisõnad: [S, sõnaliigi lisa (com v prop), sõna algvorm,
# sõnade arv lauses, lause nr, koht lauses, süntaks, arv, kääne, ülemusverbi nr, kaugus viitealusest (kahe sõna vahel olevate sõnade arv)]
    def referenceInfoIntoList(line,pronoomeniInfo):
        if re.search('.+ [S] .+', line):
            list = ['XXX']*11
            list[0] = 'S'
            r = re.search('.+ [S] (com|prop) .+', line)
            if r:
                list[1] = r.group(1)
            list = commonInfoIntoList(list, line)
            s = re.match('.+ (nom|gen|part|ill|in|el|all|ad|abl|tr|term|es|abes|kom|adit) .+', line)
            if s:
                list[8] = s.group(1)
            proLauseNr = int(pronoomeniInfo[3])
            proPositsioonLauses = int(pronoomeniInfo[4])
            anaLauseNr = int(list[4])
            anaPositsioonLauses = int(list[5])
            list[10] = distanceCalculator(proLauseNr, anaLauseNr, proPositsioonLauses, anaPositsioonLauses)
            return list
# Kui on N (numeraalid v nimisõnad): [sõnaliik (N), sõnaliigi lisa (card v ord), sõna algvorm,
# sõnade arv lauses, lause nr, koht lauses, süntaks, arv, kääne, esitusviis(digit, roman, l), ülemusverbi nr, kaugus viitealusest (kahe sõna vahel olevate sõnade arv)]
        elif re.search('.+ [N] .+', line):
            list = ['XXX'] * 12
            list[0] = 'N'
            r = re.search('.+ [N] (card|ord) .+', line)
            if r:
                list[1] = r.group(1)
            list = commonInfoIntoList(list, line)
            s = re.match('.+ (nom|gen|part|ill|in|el|all|ad|abl|tr|term|es|abes|kom|adit) .+', line)
            if s:
                list[8] = s.group(1)
            y = re.match('.+ (digit|l|roman) .+', line)
            if y:
                list[10] = y.group(1)
            proLauseNr = int(pronoomeniInfo[3])
            proPositsioonLauses = int(pronoomeniInfo[4])
            anaLauseNr = int(list[4])
            anaPositsioonLauses = int(list[5])
            list[11] = distanceCalculator(proLauseNr, anaLauseNr, proPositsioonLauses, anaPositsioonLauses)
            return list
    #A: [A, pos/comp/super, SNVRM, AOW, STNR, koht lauses, sõntaks, arv, kääne, ülemusverb, kaugus]
        elif re.search('.+ [A] .+', line):
            list = ['XXX'] * 11
            list[0] = 'A'
            r = re.search('.+ [A] (pos|comp|super) .+', line)
            if r:
                list[1] = r.group(1)
            list = commonInfoIntoList(list, line)
            s = re.match('.+ (nom|gen|part|ill|in|el|all|ad|abl|tr|term|es|abes|kom|adit) .+', line)
            if s:
                list[8] = s.group(1)
            proLauseNr = int(pronoomeniInfo[3])
            proPositsioonLauses = int(pronoomeniInfo[4])
            anaLauseNr = int(list[4])
            anaPositsioonLauses = int(list[5])
            list[10] = distanceCalculator(proLauseNr, anaLauseNr, proPositsioonLauses, anaPositsioonLauses)
            return list
#Määrsõnad: [D, XXX, algvorm, arv lauses, lause nr. koht lauses, süntaks
            #XXX, XXX, ülemusverb, kaugus
        elif re.search('.+ [D] .+', line):
            list = ['XXX'] * 11
            list[0] = 'D'
            list = commonInfoIntoList(list,line)
            proLauseNr = int(pronoomeniInfo[3])
            proPositsioonLauses = int(pronoomeniInfo[4])
            anaLauseNr = int(list[4])
            anaPositsioonLauses = int(list[5])
            list[10] = distanceCalculator(proLauseNr, anaLauseNr, proPositsioonLauses, anaPositsioonLauses)
            return list
        elif re.search('.+ [Y] .+', line):
            list = ['XXX'] * 11
            list[0] = 'Y'
            r = re.search('.+ [Y] (nominal|adjectival|adverbial|verbal)', line)
            if r:
                list[1] = r.group(1) #nimi-,omadus-,määr- või tegusõnalühend.
            list = commonInfoIntoList(list,line)
            s = re.search('.+ (nom|gen|part|ill|in|el|all|ad|abl|tr|term|es|abes|kom|adit) .+', line)
            if s:
                list[8] = s.group(1) # kääne
            proLauseNr = int(pronoomeniInfo[3])
            proPositsioonLauses = int(pronoomeniInfo[4])
            anaLauseNr = int(list[4])
            anaPositsioonLauses = int(list[5])
            list[10] = distanceCalculator(proLauseNr, anaLauseNr, proPositsioonLauses, anaPositsioonLauses)
            return list
# Verbi puhul on listis: [V, (main|aux|mod), word form, amount of words, sentence number, (indic|imper|cond|inf|partic|ger|sup|quot),
        # (pres|impf|past), (ps1|ps2|ps3), (sg|pl), (ps|imps), (af), (neg), (ill|in|el|tr|abes), position in sentence, syntax, ülemusverb, kaugus]
        elif re.search('.+ [V] .+', line):
            list = ["XXX"]*16
            list[0] = "V"
            r = re.search('.+ (main|aux|mod) .+', line)
            if r:
                list[1] = r.group(1)
            m = re.search('.+STNR([0-9]+) AOW([0-9]+) SNVRM:([^ ]+)', line)
            if m:
                list[2] = (m.group(3).lower())  # word form
                anaLauseNr = int(m.group(1))
                list[3] = (m.group(2))  # amount of words
                list[4] = (m.group(1))  # sentence number
            r = re.search('.+ (indic|imper|cond|inf|partic|ger|sup|quot) .+', line)
            if r:
                list[5] = r.group(1)
            r = re.search('.+ (pres|impf|past) .+', line)
            if r:
                list[6] = r.group(1)
            r = re.search('.+ (ps1|ps2|ps3) .+', line)
            if r:
                list[7] = r.group(1)
            r = re.search('.+ (sg|pl) .+', line)
            if r:
                list[8] = r.group(1)
            r = re.search('.+ (ps|imps) .+', line)
            if r:
                list[9] = r.group(1)
            r = re.search('.+ (af) .+', line)
            if r:
                list[10] = r.group(1)
            r = re.search('.+ (neg) .+', line)
            if r:
                list[11] = r.group(1)
            r = re.search('.+ (ill|in|el|tr|abes) .+', line)
            if r:
                list[12] = r.group(1)
            g = re.search('.+@(.+) #([0-9]+)->([0-9]+) ', line)
            if g:
                anaPositsioonLauses = int(g.group(2))
                list[13] = (g.group(2))  # position
                list[14] = (g.group(1))  # syntax
                list[15] = (g.group(3))  # syntax
            proLauseNr = int(pronoomeniInfo[3])
            proPositsioonLauses = int(pronoomeniInfo[4])
            list.append(distanceCalculator(proLauseNr, anaLauseNr, proPositsioonLauses, anaPositsioonLauses))
            return list
        else:
            list = []
            if re.search('.+ [P] .+', line):
                list = pronomenInfoIntoList(line)
                proLauseNr = int(pronoomeniInfo[3])
                proPositsioonLauses = int(pronoomeniInfo[4])
                anaPositsioonLauses = int(list[4])
                anaLauseNr = int(list[3])
                list.append(distanceCalculator(proLauseNr, anaLauseNr, proPositsioonLauses, anaPositsioonLauses))
            else:
                list.append(line)
            return list

    # Get all pronomens with their references into a list with two elements.
    # First being the pronomen info, second reference(s).
    for line in info:
                if re.match('.+{Pronoomen}', line):
                    infoList = [[], []]
                    infoList[0] = pronomenInfoIntoList(line)
                    m = re.search('{Coref:([^}]+)}', line)
                    if m:  # If Coref exists
                        numbers = m.group(1)
                        listOfReferences = []
                        byOneReference = numbers.split(",")
                        for item in byOneReference:
                            splitted = item.split(".")
                            sentenceNr = splitted[0]
                            wordNr = splitted[1]
                            for anotherLine in info:
                                if re.search(".+STNR" + sentenceNr + " ", anotherLine):
                                    if re.search(".+#" + wordNr + "->[0-9]", anotherLine):
                                        listOfReferences.append(referenceInfoIntoList(anotherLine, infoList[0]))
                        infoList[1] = listOfReferences
                    else:  # if coref doesn't exist
                        infoList[1] = ["There's no reference!"]
                    material[infoList[0][7]].append(infoList)

    print("Lõpetasin faili:" + path)

def headlinesForExcel(worksheet):
    worksheet.write(0, 0, 'Indeks')
    worksheet.write(0, 1, 'Viitealuste arv')
    worksheet.write(0, 2, 'Pro')
    worksheet.write(0, 3, 'Sõnade arv lauses')
    worksheet.write(0, 4, 'Lause number')
    worksheet.write(0, 5, 'Koht lauses')
    worksheet.write(0, 6, 'Süntaks')
    worksheet.write(0, 7, 'Arv')
    worksheet.write(0, 8, 'Kääne')
    worksheet.write(0, 9, 'See teine asi')
    worksheet.write(0, 10, 'Pööre')
    worksheet.write(0, 11, 'Ülemusverb')

    worksheet.write(0, 13, 'VSõnaliik')
    worksheet.write(0, 14, 'VAlgvorm')
    worksheet.write(0, 15, 'VSõnade arv lauses')
    worksheet.write(0, 16, 'VLause nr')
    worksheet.write(0, 17, 'VKoht lauses')
    worksheet.write(0, 18, 'VSüntaks')
    worksheet.write(0, 19, 'VArv')
    worksheet.write(0, 20, 'VKaugus pronoomenist')
    worksheet.write(0, 21, 'VÜlemusverb')

def coreferenceInfoToTheRow(viide, worksheet, row, col):
    if (viide[0] == 'N'):
        worksheet.write(row, col, str(viide[0]))  # sõnaliik
        worksheet.write(row, col + 1, str(viide[2]))  # algvorm
        worksheet.write(row, col + 2, str(viide[3]))  # sõnade arv
        worksheet.write(row, col + 3, str(viide[4]))  # lause nr
        worksheet.write(row, col + 4, str(viide[5]))  # koht lauses
        worksheet.write(row, col + 5, str(viide[6]))  # süntaks
        worksheet.write(row, col + 6, str(viide[7]))  # arv
        worksheet.write(row, col + 7, str(viide[-1]))  # kaugus
        worksheet.write(row, col + 8, str(viide[9]))  # ülemusverb
        worksheet.write(row, col + 9, str(viide[1]))  # sõnaliigi lisa
        worksheet.write(row, col + 10, str(viide[8]))  # kääne
        worksheet.write(row, col + 11, str(viide[10]))  # esitusviis
    elif (viide[0] == 'V'):
        worksheet.write(row, col, str(viide[0]))  # sõnaliik
        worksheet.write(row, col + 1, str(viide[2]))  # algvorm
        worksheet.write(row, col + 2, str(viide[3]))  # sõnade arv
        worksheet.write(row, col + 3, str(viide[4]))  # lause nr
        worksheet.write(row, col + 4, str(viide[13]))  # koht lauses
        worksheet.write(row, col + 5, str(viide[14]))  # süntaks
        worksheet.write(row, col + 6, str(viide[8]))  # arv
        worksheet.write(row, col + 7, str(viide[-1]))  # kaugus
        worksheet.write(row, col + 8, str(viide[15]))  # ülemusverb
        worksheet.write(row, col + 9, str(viide[1]))  # (main|aux|mod)
        worksheet.write(row, col + 10, str(viide[5]))  # (indic|imper|cond|inf|partic|ger|sup|quot)
        worksheet.write(row, col + 11, str(viide[6]))  # (pres|impf|past)
        worksheet.write(row, col + 12, str(viide[7]))  # (ps1|ps2|ps3)
        worksheet.write(row, col + 13, str(viide[9]))  # (ps|imps)
        worksheet.write(row, col + 14, str(viide[10]))  # (af)
        worksheet.write(row, col + 15, str(viide[11]))  # (neg)
        worksheet.write(row, col + 16, str(viide[12]))  # (ill|in|el|tr|abes)
    elif (viide[0] == 'P'):
        worksheet.write(row, col, str(viide[0]))  # sõnaliik
        worksheet.write(row, col + 1, str(viide[1]))  # algvorm
        worksheet.write(row, col + 2, str(viide[2]))  # sõnade arv
        worksheet.write(row, col + 3, str(viide[3]))  # lause nr
        worksheet.write(row, col + 4, str(viide[4]))  # koht lauses
        worksheet.write(row, col + 5, str(viide[5]))  # süntaks
        worksheet.write(row, col + 6, str(viide[6]))  # arv
        worksheet.write(row, col + 7, str(viide[-1]))  # kaugus
        worksheet.write(row, col + 8, str(viide[11]))  # ülemusverb
        worksheet.write(row, col + 9, str(viide[9]))  # (inter rel|dem|pers|pos|det ref|det)
        worksheet.write(row, col + 10, str(viide[8]))  # kääne
        worksheet.write(row, col + 11, str(viide[10]))  # pööre
    elif (viide[0] == 'Y') or (viide[0] == 'A') or (viide[0] == 'S') or (viide[0] == 'D'):
        worksheet.write(row, col, str(viide[0]))  # sõnaliik
        worksheet.write(row, col + 1, str(viide[2]))  # algvorm
        worksheet.write(row, col + 2, str(viide[3]))  # sõnade arv
        worksheet.write(row, col + 3, str(viide[4]))  # lause nr
        worksheet.write(row, col + 4, str(viide[5]))  # koht lauses
        worksheet.write(row, col + 5, str(viide[6]))  # süntaks
        worksheet.write(row, col + 6, str(viide[7]))  # arv
        worksheet.write(row, col + 7, str(viide[-1]))  # kaugus
        worksheet.write(row, col + 8, str(viide[9]))  # ülemusverb
        worksheet.write(row, col + 9, str(viide[1]))  # sõnaliigi lisa
        worksheet.write(row, col + 10, str(viide[8]))  # kääne
    elif re.search('.+ reference!', str(i[1])):
        worksheet.write(row, col, "")
    else:
        worksheet.write(row, col, str(viide[0]))

def pronomenInfoIntoTheRow(pronoomeniIsiklikIndeks, worksheet, i, row):
    viitealusteArv = len(i[1])
    if re.search('.+ reference!', str(i[1])):
        viitealusteArv = 0
        # pronoomeni info.
    worksheet.write(row, 0, pronoomeniIsiklikIndeks)
    worksheet.write(row, 1, viitealusteArv)
    worksheet.write(row, 2, i[0][1])  # sõnakuju
    worksheet.write(row, 3, i[0][2])  # sõnade arv lauses
    worksheet.write(row, 4, i[0][3])  # lause nr
    worksheet.write(row, 5, i[0][4])  # koht lauses
    worksheet.write(row, 6, i[0][5])  # süntaks
    worksheet.write(row, 7, i[0][6])  # arv
    worksheet.write(row, 8, i[0][8])  # kääne
    worksheet.write(row, 9, i[0][9])  # muu
    worksheet.write(row, 10, i[0][10])  # pööre
    worksheet.write(row, 11, i[0][11])  # ülemusverb

#Alustame Exceli faili loomisega.
import xlsxwriter
workbook = xlsxwriter.Workbook('AnafoorideAnalyys.xlsx')

for pronoomen in pronoomenid:
    worksheet = workbook.add_worksheet(pronoomen + ' asendussõnad')
    worksheetWithTotal = workbook.add_worksheet(pronoomen + ' viitealused')
    # Start from the second cell. Rows and columns are zero indexed.
    row = 1
    col = 13
    col2 = 13
    row2 = 1

    vastused = material[pronoomen]
    tabelisse = ()
    anaAndmed = []
    headlinesForExcel(worksheet) #write the first row of the sheet (the headlines for the columns)
    headlinesForExcel(worksheetWithTotal)

    pronoomeniIsiklikIndeks = 1
    for i in vastused:
        pronomenInfoIntoTheRow(pronoomeniIsiklikIndeks, worksheet, i, row) #first worksheet with anaphoras.

        for viide in i[1]:
            coreferenceInfoToTheRow(viide, worksheet,  row, col) #all info in one row
            if not (re.search('.+ reference!', str(i[1]))):
                pronomenInfoIntoTheRow(pronoomeniIsiklikIndeks, worksheetWithTotal, i, row2) #second worksheet with full list of coreferences
                coreferenceInfoToTheRow(viide, worksheetWithTotal,  row2, col2) #all corefeneces in one column
                col += 19
                row2 += 1
        col = 13
        row += 1
        pronoomeniIsiklikIndeks += 1

workbook.close()
print("Tehtud.")