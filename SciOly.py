# from js import getCsv
# from pyodide import to_js
import math
import csv
import copy


from nodes import Person, Course, ExtraCurricular, Event

# how big are teams?
TEAMSIZE = 17
# how much margin of error do we want?
# smaller margin lowers probability of success
PERCENTDIFF = 0.25
# how many events do we ask people to rank?
NUMCHOICES = 15
# total events
TOTALEVENTS = 23
# minimum number of events each person should be in
MINEVENTS = 4
# how can we relate skills in LFA science courses and Scioly events?
# Biology, Chemistry, Environmental Sciences, Physics
# almost all physics-related events are build events so
# I didn't bother creating a build type, since it falls under physics
EVENTTYPES = ["Bio", "Chem", "Env", "Phys"]
# some events like codebusters or EXPD don't have classes that relate to them
# we assign these the tag "Any" since really any/no science helps learn them
# I use a variable here to just more easily keep track of "any"
ANY = "Any"
# this variable represents how I represent the block time slot
# for build events in the csvs
BUILDBLOCK = "X"
# this variable represents a list of blocks.
# It is used purely for generating output.
BLOCKS = ["A", "B", "C", "D", "E", BUILDBLOCK]

# maxcount sets a limit for how many possibilities the function will explore.
# This is done, because the distribution of people on JV is subject to softer
# constraints than on varsity. Since the program interates through multiple
# possibilities, this can cause the program to run far too long otherwise
MAXCOUNT = 1

# SciOlyFinal.py is the name of this program
# data.csv contains all the data gained from the google form
# events.csv contains any info about the events themselves
# classes.csv contains info about courses offered at LFA
# extracurriculars.csv names of extracurricular options listed in the form
# varsity.csv is a hand-selected group of scioly members that
# the captains think are a good fit for varsity at the start of the year
# varsity.csv should be a list of emails, not names, in no particular order
# ideally, the coaches should identify exactly 15 individuals
# who they want on varsity
# if they have more then they should limit who they input into
# the program for varsity.csv
# you could always change up the people and rerun the program


x = 47


def main(data, classesDefined, eventsDefined, ecs, varsityDefined):
    # saves data we want to return
    toRet = ""
    # loads csv data
    events = loadEvents(eventsDefined)
    firstEventsCopy = copy.deepcopy(events)
    classes, extracurriculars = loadClassesExtras(
        classesDefined,
        ecs)
    people = loadData(data, events, classes, extracurriculars)
    # eventNames = generateEventNames(events)
    varsity = loadVarsity(varsityDefined, people)
    numSpots = teamReq(events)
    if len(varsity) > 0:
        # total number of spots
        # average number of people that should be in an event
        averagePeoplePerEvent = numSpots/len(varsity)
        # create a dictionary of weights we can access later
        # to save time recalculating values
        dictionary = generateWeightDict(varsity, events, True)
        # initialize varsity team
        initializeSuperDomains(varsity, events)
        eventsCopy = copy.deepcopy(events)
        varsityCopy = copy.deepcopy(varsity)
        sum = 0
        topChoices = initializeByChoice(
            varsity,
            events,
            int(averagePeoplePerEvent) + 1
            )
        sortDomains(events, dictionary)
        # stick to maxSum = 1 or 2
        # maxSum = 2 gives better result, but takes longer
        # approximately 6 minutes longer or about 93x longer
        # In short, maxSum dictates how many possibilities we iterate through
        maxSum = 1
        v, e = backtrack(
            varsity,
            events,
            numSpots,
            dictionary,
            0,
            0,
            0,
            maxSum,
            False)[
            0:2
        ]
        while e is None and topChoices < NUMCHOICES:
            varsity = copy.deepcopy(varsityCopy)
            events = copy.deepcopy(eventsCopy)
            topChoices = initializeByChoice(varsity, events, topChoices+1)
            sortDomains(events, dictionary)
            v, e = backtrack(
                varsity, events, numSpots, dictionary, 0, 0, 0, maxSum, False
            )[0:2]

        # I use finalizeJV here, in case the condition where everyone
        # should be in 5 events is active
        v, e = finalizeJV(
            v, e, teamReq(events)/TOTALEVENTS + 2,
            teamReq(events)/TOTALEVENTS
            )
        # this case only occurs if you can't assign everyone
        # when considering all of their top choices
        if e is None and topChoices == NUMCHOICES:
            toRet = "No solutions were found for the varsity team \n"
        events = e
        varsity = v
        # updateDomains just cleans everything up
        updateDomains(varsity, events, topChoices)
        toRet = returnOutput(varsity, events, toRet)

        events = firstEventsCopy
        juniorVarsity = list()
        valid = True
        for p in people:
            valid = True
            for pe in varsity:
                if p.getEmail() == pe.getEmail():
                    valid = False
                    break
            if valid:
                juniorVarsity.append(p)
    else:
        juniorVarsity = people

    if len(juniorVarsity) >= TEAMSIZE:
        juniorVarsityCopy = copy.deepcopy(juniorVarsity)
        averagePeoplePerEvent =\
            MINEVENTS*len(juniorVarsity)/TOTALEVENTS
        # min and max provide an upper and lower bound of
        # how many people should be in an event
        # this will mainly be used for non-varsity.
        # There should be between 1 - PERCENTDIFF and 1 + PERCENTDIFF %
        # of the average people per event.
        minNumPerEvent = int(averagePeoplePerEvent*(1-PERCENTDIFF))
        maxNumPerEvent = int(averagePeoplePerEvent*(1+PERCENTDIFF))

        # pretty much same code as for varsity now.
        # bruh I don't use minNumPerEvent, make sure to code that in...
        sum = 0
        for e in events:
            if e.getNumPeople() < minNumPerEvent:
                e.setNumPeople(minNumPerEvent)
            sum += e.getNumPeople()
        dictionary = generateWeightDict(juniorVarsity, events, False)
        initializeSuperDomains(juniorVarsity, events)
        eventsCopy = copy.deepcopy(events)
        topChoices = initializeByChoice(
            juniorVarsity, events, int(averagePeoplePerEvent) + 1
        )
        sortDomains(events, dictionary)

        maxSumJV = 1
        jv, e = backtrack(
            juniorVarsity,
            events,
            sum,
            dictionary,
            0,
            0,
            0,
            maxSumJV,
            True)[
            0:2
        ]
        while e is None and topChoices < NUMCHOICES:
            juniorVarsity = copy.deepcopy(juniorVarsityCopy)
            events = copy.deepcopy(eventsCopy)
            topChoices = initializeByChoice(
                juniorVarsity,
                events,
                topChoices + 1)
            sortDomains(events, dictionary)
            jv, e = backtrack(
                juniorVarsity, events, sum, dictionary, 0, 0, 0, maxSumJV, True
            )[0:2]
        if e is None and topChoices == NUMCHOICES:
            toRet += "No solutions were found for the junior varsity team"
        else:
            juniorVarsity, events = finalizeJV(
                jv, e, maxNumPerEvent, averagePeoplePerEvent
            )
            # updateDomains(juniorVarsity, events, topChoices)
            # juniorVarsity, events = finalizeJV(jv, e, maxNumPerEvent)
            toRet = returnOutput(juniorVarsity, events, toRet)
    else:
        toRet += "There are too few people to create a junior varsity team"

    return toRet

# parameters:
# clss is a csv file containing the courses
# extr is a csv file containing the extracurriculars
# returns a list of extracurricular objects


def loadClassesExtras(clss, extr):
    classes = list()
    extracurriculars = list()
    for num, rowx in enumerate(clss.splitlines()):
        row = rowx.split(",")
        # class name
        name = row[0]
        # class weight - APs and Post-APs are given a weight of 2
        # while normal/advanced classes and electives are given weight 1
        weight = float(row[1])
        # what subjects do these classes relate to
        # stores data using a binary representation
        edit = row[2]
        edit = edit.replace(' ', '')
        edit = edit.split(',')
        subjects = 0
        for i in range(len(EVENTTYPES)):
            if EVENTTYPES[i] in edit:
                subjects += math.pow(2, i)
        course = Course(name, weight, int(subjects), num)
        classes.append(course)
        for num, rowx in enumerate(extr.splitlines()):
            row = rowx.split(",")
            extracurriculars.append(ExtraCurricular(row[0], num))
    return classes, extracurriculars


# parameters:
# evnts is a csv file containing the events
# returns a list of event objects
def loadEvents(evnts):
    events = list()
    for num, rowx in enumerate(evnts.splitlines()):
        row = rowx.split(",")
        # event name, number of people per event, and time slot
        # (X means can be any time)
        name = row[0]
        numPeople = int(row[1])
        block = row[2][0]
        # what subjects do these events relate to
        # stores data using a binary representation
        edit = row[3]
        edit = edit.replace(' ', '')
        edit = edit.split(',')
        subjects = 0
        # if (ANY not in edit):
        #    for i in range(len(EVENTTYPES)):
        #        if (EVENTTYPES[i] in edit):
        #            subjects += math.pow(2, i)
        evnt = Event(name, numPeople, block, int(subjects), num)
        events.append(evnt)
    return events


# parameters:
# evnts is a list of event objects
# returns the number of positions needed to fill a team
def teamReq(evnts):
    size = 0
    for event in evnts:
        size += event.getNumPeople()
    return size


# parameters:
# data is a csv containing data about the people
# events is a list of event objects
# classes is a list of class objects
# extra is a list of extracurricular objects
# returns a list of person objects
def loadData(data, events, classes, extra):

    info = list()

    for rowx in data.splitlines()[1:]:
        rowy = rowx.replace(", ", "^ ")
        row = rowy.split(",")
        # replace with better method

        # email row[1]
        email = row[1].lower()
        # name row[2]
        name = row[2]
        # grade row[3]
        grade = 9.0
        if (row[3] == "Senior"):
            grade = 12.0
        elif (row[3] == "Junior"):
            grade = 11.0
        elif (row[3] == "Sophomore"):
            grade = 10.0
        elif (row[3] == "Freshman"):
            grade = 9.0
        # Previous classes row[4]
        # converts each class to a number, so its easier to keep track of
        edit = row[4]
        edit = edit.split('^ ')
        classList = list()
        for cls in classes:
            if (cls.getName() in edit):
                classList.append(cls)
        # currently taking classes row[5]
        edit = row[5]
        edit = edit.split('^ ')
        currentList = list()
        for cls in classes:
            if (cls.getName() in edit):
                currentList.append(cls)
        # Commitment row[6]
        commitment = float(row[6])
        # Clubs and extra-curriculars row[7]
        edit = row[7]
        edit = edit.split('^ ')
        extraCurriculars = 0.0
        for extr in extra:
            if (extr.getName() in edit):
                extraCurriculars += 1.0
        # years at LFA scioly row[8]
        yearsLFA = float(row[8])
        # years doing scioly otherwise row[9]
        yearsNotLFA = float(row[9])
        # 1st-xth choice row[10]-row[10+x]
        # converts each event to a number, so its easier to keep track of
        choices = list()
        for i in range(NUMCHOICES):
            for evnt in events:
                if (row[10+i] == evnt.getName()):
                    if (evnt.getId() not in choices):
                        choices.append(evnt.getId())
                    else:
                        for evnt in events:
                            if (evnt.getId() not in choices):
                                choices.append(evnt.getId())
                                break
        # num events that people want to be in row[19]
        numEvents = float(row[10+NUMCHOICES][0:1])
        # over-riding this, since the average number of events per person
        # works out to be around 3.2.
        # We overfill, because having backups is better
        # than having too few people
        if (numEvents < MINEVENTS):
            numEvents = MINEVENTS
        p = Person(
            email,
            name,
            grade,
            classList,
            currentList,
            commitment,
            extraCurriculars,
            yearsLFA,
            yearsNotLFA,
            choices,
            numEvents,
        )
        info.append(p)

    # We don't track partners in the data,
    # since the same two people may not be in the same events
    # every competition. WIDI is an exception
    # but we'd probably let coaches swap a few things
    # to make that work

    return info


# parameters:
# events is a list of event objects
# returns list of strings that are event names
def generateEventNames(events):
    eventNames = list()
    for event in events:
        eventNames.append(event.getName())
    return eventNames


# parameters:
# names is a csv of the names of people on varsity
# people is a list of person objects
# returns the collection of emails as a list of strings
def loadVarsity(names, people):
    varsity = list()
    for rowx in names.splitlines():
        row = rowx.split(",")
        email = row[0]
        for person in people:
            if email == person.getEmail():
                varsity.append(person)
                break
    return varsity


# calculate the "weight" we assign for a certain person in a certain event
# person is an object
# event is an id
# parameters:
# person is a person object
# events is a list of event objects
# event is an event object
def calculateWeight(person, events, event):
    # these are how much each category should weigh into our decision of
    # how important it is for a person to be in this event
    classFactor = 1
    totalClassFactor = 0.01
    commitmentFactor = 0.7
    ecFactor = 0.2
    expFactor = 0.02
    choiceFactor = 1.4
    currentFactor = 0.3
    notFactor = 0.5

    # these are the weights calculated per person
    if event in person.getChoices():
        choiceWeight = math.pow(choiceFactor,
                                float(
                                    NUMCHOICES -
                                    person.getChoices().index(event)
                                ))
    else:
        return 0

    classWeight = totalClassFactor * len(
        person.getPrevCourses()
    ) + currentFactor * totalClassFactor * len(person.getCurrentCourses())
    commitmentWeight = commitmentFactor*person.getCommitment()
    ecWeight = ecFactor * (1 + person.getExtracurriculars())
    expWeight = expFactor * (1 + person.getYearsLFA())
    if person.getYearsNotLFA() > 0:
        expWeight += notFactor

    # calculating classWeight by disecting binary numbers
    eventBin = bin(events[event].getSubjects()).replace("0b", "")
    while len(eventBin) < len(EVENTTYPES):
        eventBin = "0" + eventBin
    for cls in person.getPrevCourses():
        clsBin = bin(cls.getSubjects()).replace("0b", "")
        while len(clsBin) < len(EVENTTYPES):
            clsBin = "0" + clsBin
        for i in range(len(clsBin)):
            if clsBin[i] == eventBin[i] and eventBin[i] == "1":
                classWeight += classFactor*cls.getWeight()
                break
    for cls in person.getCurrentCourses():
        clsBin = bin(cls.getSubjects()).replace("0b", "")
        while len(clsBin) < len(EVENTTYPES):
            clsBin = "0" + clsBin
        for i in range(len(clsBin)):
            if clsBin[i] == eventBin[i] and eventBin[i] == "1":
                classWeight += currentFactor*classFactor*cls.getWeight()
                break

    totalWeight = (
        choiceWeight * (
            classWeight
            + ecWeight
            + expWeight
            + commitmentWeight
            ))
    return round(totalWeight)


# Generates a dictionary of weights
# For putting any person in any event
# parameters:
# people is a list of people objects
# events is a list of event objects
# isVarsity is a boolean used for testing
def generateWeightDict(people, events, isVarsity):
    dictionary = dict()
    sizes = dict()
    for evnt in events:
        sizes[evnt.getId()] = 0
        for person in people:
            if evnt.getId() in person.choices:
                sizes[evnt.getId()] += 1
    for person in people:
        for event in events:
            dictionary[person.getEmail() + str(event.getId())] = round(
                calculateWeight(person, events, event.getId())
            )

    var = ""
    if isVarsity:
        var = "Varsity"

    # this document is purely for testing/debugging
    # and seeing if weights should be changed
    with open("./Dictionary" + var + ".csv", 'w') as file:
        writer = csv.writer(file)
        header = ["Name/Event"]
        for event in events:
            header.append(event.getName())
        writer.writerow(header)
        for person in people:
            email = person.getEmail()
            row = [person.getName()]
            for ind in range(len(events)):
                row.append(dictionary[email + str(ind)])
            writer.writerow(row)
    return dictionary


# fills the peoples' superDomains with each person's top events
# we can remove peoples' superdomains and just replace them with choices
# fills the events' superDomains with each person who has that event ranked
# if not enough people want to do the event so it can be filled,
# we reduce the maximum number of people needed for the event
# parameters:
# people is a list of person objects
# events is a list of event objects
# returns true to show it worked
def initializeSuperDomains(people, events):
    for person in people:
        for i in range(NUMCHOICES):
            evnt = person.getChoices()[i]
            person.appendSuperDomain(evnt)
            events[evnt].appendSuperDomain(person.getEmail())
    for evnt in events:
        if len(evnt.getSuperDomain()) < evnt.getNumTruePeople():
            evnt.setNumPeople(len(evnt.getSuperDomain()))
    return True


# this puts everyone into their top events without block conflicts
# however it only considers their first topChoices choices
# since we want to try and limit the number of people who get
# their last choices.
# These are stored in peoples' and events' domains.
# Additionally, if relatively few people want to do a certain event
# we ignore the topChoices parameter for that event
# and put everyone in the domain.
# If we cannot fill every event's domain using only
# The first TopChoices choices, we retry with TopChoices+=1
# parameters:
# people is a list of person objects
# events is a list of event objects
# topChoices is a number
# topChoices is returned for debugging purposes
def initializeByChoice(people, events, topChoices):
    for evnt in events:
        evnt.setDomain(list())
    for person in people:
        person.setDomain(list())
        for i in range(topChoices):
            evnt = person.getChoices()[i]
            person.appendDomain(evnt)
            events[evnt].appendDomain(person.getEmail())
    if topChoices == NUMCHOICES:
        return topChoices
    for evnt in events:
        if len(evnt.getSuperDomain()) <= evnt.getNumPeople()+1:
            toUpdate = [e for e in evnt.getSuperDomain() if
                        e not in evnt.getDomain()]
            for person in toUpdate:
                for p in people:
                    if p.getEmail() == person:
                        p.appendDomain(evnt.getId())
                        break
            evnt.setDomain(copy.deepcopy(evnt.getSuperDomain()))
        if len(evnt.getDomain()) < evnt.getNumPeople():
            return initializeByChoice(people, events, topChoices+1)
    return topChoices


# this should "clean up" each team
# it will make sure that 15 people cover the events
# this method looks at the least filled events and empties them
# then it looks at the first two people in each event
# and performs the iteration for each person
# parameters:
# people is a list of person objects
# events is a list of event objects
# numSpots is an integer
# dictionary is a dictionary
# iteration is an integer used for debugging
# depth is an integer used for debugging
# maxSum is an integer used to cap runtime
# isJV is a boolean
def backtrack(
        varsity,
        events,
        numSpots,
        dictionary,
        iteration,
        depth,
        totalCount,
        maxSum,
        isJV,
        ):

    # for debugging
    iteration += 1
    depth += 1
    complete = 0
    for evnt in events:
        if len(evnt.getPeople()) > 0:
            complete += 1
    if complete == TOTALEVENTS or totalCount >= MAXCOUNT:
        totalCount += 1
        return (varsity, events, rankResult(events, dictionary),
                iteration, totalCount)
    evnt = selectUnassignedVar(events)

    combos = generateCombinations(
        0, len(events[evnt].getDomain()), events[evnt].getNumPeople()
        )

    varsityCopy = copy.deepcopy(varsity)
    eventsCopy = copy.deepcopy(events)

    bestResultValue = 0
    bestVarsity = None
    bestEvents = None

    length = events[evnt].getNumPeople()
    maxx = (length*length - length)/2 + maxSum
    jvEdit = len(events)-len(BLOCKS)-2
    if isJV and depth >= jvEdit:
        maxx -= maxSum

    for combo in combos:
        sum = 0
        for num in combo:
            sum += num
        if sum > maxx:
            # generally speaking, the sum of the different indices
            # in combo should be less than 3 for events with 2 people
            # & less than 5 for events with 3
            # this means that out of the remaining people in the domain
            # that their ranked weights should sum to no more than 3.
            continue
        assignment = list()
        for num in combo:
            # We have to do this, because when copying the copies
            # We need to look at the new evnt, instead of the old one
            assignment.append(events[evnt].getDomain()[num])
        events[evnt].setPeople(assignment)
        if ac3(events, evnt, assignment, varsity) is not False:
            resultVar, resultEv, resultValue, iteration, totalCount =\
                backtrack(
                    varsity,
                    events,
                    numSpots,
                    dictionary,
                    iteration,
                    depth,
                    totalCount,
                    maxSum,
                    isJV
                )
            # compares each valid result to the best result
            if resultEv is not None:
                if resultValue > bestResultValue:
                    bestResultValue = resultValue
                    bestVarsity = copy.deepcopy(resultVar)
                    bestEvents = copy.deepcopy(resultEv)
        # reset people and events using the copies we made earlier,
        # so other results can be tested.
        varsity = copy.deepcopy(varsityCopy)
        events = copy.deepcopy(eventsCopy)
    return bestVarsity, bestEvents, bestResultValue, iteration, totalCount


# This method checks that a valid solution still exists
# given that we've assigned some people to some events
# it does this by removing any conflicts created by placing them
# in these events, checking if every event
# still has enough people to fill it up.
# If a person reaches their maximum number of events, it removes
# them from consideration also.
# Lastly, it physically places people into their events in the
# person class.
# parameters:
# events is the list of events
# evnt is the event that was modified most recently
# assignment are the people added to this event
# people is the list of people
def ac3(events, evnt, people, varsity):

    truePeople = list()
    for person in people:
        for p in varsity:
            if p.getEmail() == person:
                truePeople.append(p)
                break

    for person in truePeople:
        person.removeDomain(evnt)
        events[evnt].removeDomain(person.getEmail())
        person.appendEvents(evnt)
        if events[evnt].getBlock() != BUILDBLOCK:
            toRemove = list()
            for e in person.getDomain():
                if events[e].getBlock() == events[evnt].getBlock():
                    events[e].removeDomain(person.getEmail())
                    toRemove.append(e)
            for e in toRemove:
                person.removeDomain(e)
        if len(person.getEvents()) >= person.getNumEvents():
            for e in person.getDomain():
                if person.getEmail() in events[e].getDomain():
                    events[e].removeDomain(person.getEmail())
            person.setDomain(list())
    # don't remove people from the rest of the domain
    # this way we can preserve valid preferences for them
    # which we output later (for human intervention)

    for e in events:
        if len(e.getDomain()) < e.numPeople and len(e.getPeople()) == 0:
            return False


# generates all combinations of total number of elements
# between min and max
# parameters: all are integers
def generateCombinations(min, max, total):
    if (total == 0):
        return None
    if (min == max):
        return False
    combos = list()
    for elem in range(min, max):
        subset = generateCombinations(elem+1, max, total-1)
        if subset is None:
            combos.append([elem])
        elif subset is False:
            break
        else:
            for e in subset:
                combos.append([elem] + e)
    return combos


# this selects the event with the fewest people in its domain
# but which has no assignments yet
# and we assign people to this event first
# parameters:
# events is a list of event objects
# returns the event with the fewest people in its domain
def selectUnassignedVar(events):
    min = 10000
    minIndex = -1
    for evnt in events:
        if len(evnt.getDomain()) < min and len(evnt.getPeople()) == 0:
            min = len(evnt.getDomain())
            minIndex = evnt.getId()
    return minIndex


# this orders people by weight for each event's domain
# parameters:
# events is a list of event objects
# dictionary is a dictionary that relates weight
# and a person's desire/qualification for an event
def sortDomains(events, dictionary):
    for ev in events:
        ev.setDomain(domainValues(events, ev.getId(), dictionary))
        ev.reverseDomain()


# this orders people by weight
# highest weight is at the front
# they will be the people first considered to get cut from that event
# hopefully weighting is right
# parameters:
# events is a list of event objects
# event is a specific event
# dictionary is a dictionary that relates weight
# and a person's desire/qualification for an event
def domainValues(events, event, dictionary):
    emails = events[event].getDomain()
    weights = []
    for email in emails:
        weights.append(dictionary[email + str(event)])
    p = mergeSort(emails, weights, 0, len(weights)-1)[0]
    return p


# I recreated mergesort to sort the people by their weights
def mergeSort(people, weights, left, right):
    if left < right:
        m = int((left+right)/2)
        left, leftWeights = mergeSort(people, weights, left, m)
        right, rightWeights = mergeSort(people, weights, m+1, right)
        return merge(left, right, leftWeights, rightWeights)
    else:
        return [people[right]], [weights[right]]


# more mergesort
def merge(left, right, leftWeights, rightWeights):
    i = 0
    j = 0
    endI = len(left)
    endJ = len(right)
    arr = []
    weights = []
    while i < endI and j < endJ:
        if leftWeights[i] <= rightWeights[j]:
            arr.append(left[i])
            weights.append(leftWeights[i])
            i += 1
        else:
            arr.append(right[j])
            weights.append(rightWeights[j])
            j += 1

    while i < endI:
        arr.append(left[i])
        weights.append(leftWeights[i])
        i += 1

    while j < endJ:
        arr.append(right[j])
        weights.append(rightWeights[j])
        j += 1

    return arr, weights


# fills in jv, since we fill the jv team to min capacity
# similar to backtrack
# works by picking the best person in each event until
# all events are full
def finalizeJV(jv, events, maxNum, average):
    done = True
    for evnt in events:
        if len(evnt.getDomain()) > 0 and len(evnt.getPeople()) < maxNum:
            done = False
            break
    if done:
        return jv, events
    ev = selectUnassignedJV(events, maxNum, average)
    # just in case
    if (ev == -1):
        return jv, events
    # domain should still be preserved
    assignment = list()
    assignment.append(events[ev].getDomain()[0])
    events[ev].appendPeople(events[ev].getDomain()[0])
    ac3(events, ev, assignment, jv)
    return finalizeJV(jv, events, maxNum, average)


# fills in jv step by step
# uses an average parameter to prioiritze events
# below the average number of people
# so the team is more spread out
def selectUnassignedJV(events, max, average):
    min = 10000
    minIndex = -1
    belowAverage = False
    for evnt in events:
        if (belowAverage
                and len(evnt.getDomain()) > 0
                and len(evnt.getDomain()) < min
                and len(evnt.getPeople()) < average):
            min = len(evnt.getDomain())
            minIndex = evnt.getId()
        elif (not belowAverage
                and len(evnt.getDomain()) > 0
                and len(evnt.getDomain()) < min
                and len(evnt.getPeople()) < max):
            min = len(evnt.getDomain())
            minIndex = evnt.getId()
            if (len(evnt.getPeople()) < average):
                belowAverage = True
    return minIndex


# this cleans up peoples' domains,
# getting rid of any overlap events among their actual events
# this is mainly used to help identify
# what events people who weren't assigned their desired number of events
# can be added to
# parameters:
# people is the list of people
# topChoices is the number of choices considered
def updateDomains(people, events, topChoices):
    for person in people:
        if len(person.getEvents()) < person.getNumEvents():
            for evnt in person.getSuperDomain()[topChoices:]:
                uniqueBlock = True
                for e in person.getEvents():
                    if events[evnt].getBlock() == events[e].getBlock():
                        uniqueBlock = False
                        break
                if uniqueBlock:
                    person.appendDomain(evnt)
                    events[evnt].appendDomain(person.getEmail())


# this will create the output csv file for the varsity team
# parameters:
# people is the list of people
# events is the list of events
# isVarsity is a boolean telling us whether this is
# for the varsity or JV team
def output(people, events, isVarsity):
    var = "Varsity"
    if isVarsity is False:
        var = ""
    with open("./OutputEvents" + var + ".csv", 'w') as file:
        writer = csv.writer(file)
        header = ["Event"] + BLOCKS[:-1] + ["Build"]
        writer.writerow(header)
        for evnt in events:
            row = [evnt.getName()]
            for block in BLOCKS:
                if evnt.getBlock() == block:
                    row.append(stringifyEmails(people, evnt.getPeople()))
                else:
                    row.append("")
            writer.writerow(row)
        file.close()
    any = False
    for person in people:
        if person.getNumEvents() > len(person.getEvents()):
            any = True
            break
    if any:
        with open("./OutputPeople" + var + ".txt", 'w') as file:
            file.write(
                "The following people are in less events"
                + " than they requested originally.\n"
            )
            file.write("You may put them into certain events as backups.\n")
            any = False
            for person in people:
                if person.getNumEvents() > len(person.getEvents()):
                    any = True
                    toPrint = ""
                    if len(person.getDomain()) != 0:
                        for evnt in person.getDomain():
                            toPrint += events[evnt].getName() + ", "
                        toPrint = toPrint[:-2]
                        file.write(
                            person.getName()
                            + " would like to join "
                            + str(int(person.getNumEvents()
                                  - len(person.getEvents())))
                            + " of the following events: "
                            + toPrint
                            + "\n"
                        )
                    else:
                        file.write(
                            person.name
                            + " would like to join "
                            + str(int(person.getNumEvents()
                                  - len(person.getEvents())))
                            + " events, but all of their selected events"
                            + " conflict with their other events."
                            + "\n"
                        )
            file.close()


# this will create the output csv file for the varsity team
# parameters:
# people is the list of people
# events is the list of events
# isVarsity is a boolean telling us whether this is
# for the varsity or JV team
# This function was used back when I ran the program through the terminal
# I now use the above function
def returnOutput(people, events, varsity):
    varsity += "\n"
    for evnt in events:
        varsity += evnt.getName() + ","
        varsity += stringifyEmails(people, evnt.getPeople())
        varsity += "\n"

    any = False
    for person in people:
        if person.getNumEvents() > len(person.getEvents()):
            any = True
            break
    if any:
        varsity += "The following people are in less events"
        varsity += " than they requested originally.\n"
        varsity += "You may put them into certain events as backups.\n"

        for person in people:
            if person.getNumEvents() > len(person.getEvents()):
                any = True
                toPrint = ""
                if len(person.getDomain()) != 0:
                    for evnt in person.getDomain():
                        toPrint += events[evnt].getName() + ", "
                    toPrint = toPrint[:-2]
                    varsity += person.getName() + " would like to join "
                    varsity += str(int(person.getNumEvents()
                                   - len(person.getEvents())))
                    varsity += " of the following events: " + toPrint + "\n"
                else:
                    varsity += person.getName() + " would like to join "
                    varsity += str(int(person.getNumEvents()
                                   - len(person.getEvents())))
                    varsity += " events, but all of their selected events"
                    varsity += " conflict with their other events. \n"
    return varsity


# returns the list of names for a certain event
# parameters:
# people is the list of people
# ls is the event's attendees
def stringifyEmails(people, ls):
    output = ""
    for elem in ls:
        for person in people:
            if person.getEmail() == elem:
                output += person.getName() + ","
                break
    return output[:-1]


# returns the total weight of every decision made
# parameters:
# events is the list of events
# dictionary is the dictionary relating weight and placement
def rankResult(events, dictionary):
    totalWeight = 0.0
    for evnt in events:
        for email in evnt.getPeople():
            totalWeight += dictionary[email + str(evnt.getId())]
    return totalWeight


# if __name__ == "__main__":
#    main()
