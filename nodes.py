class Person():

    def __init__(self, email, name, grade, prevCourses, currentCourses,
                 commitment, extracurriculars, yearsLFA, yearsNotLFA,
                 choices, numEvents):
        self.email = email
        self.name = name
        self.grade = grade
        self.prevCourses = prevCourses
        self.currentCourses = currentCourses
        self.commitment = commitment
        self.extracurriculars = extracurriculars
        self.yearsLFA = yearsLFA
        self.yearsNotLFA = yearsNotLFA
        self.choices = choices
        self.numEvents = numEvents
        self.partners = list()
        self.domain = list()
        self.events = list()
        self.superDomain = list()

    def getName(self):
        return self.name

    def getEmail(self):
        return self.email

    def getDomain(self):
        return self.domain

    def getChoices(self):
        return self.choices

    def getPrevCourses(self):
        return self.prevCourses

    def getCommitment(self):
        return self.commitment

    def getCurrentCourses(self):
        return self.currentCourses

    def getExtracurriculars(self):
        return self.extracurriculars

    def getYearsLFA(self):
        return self.yearsLFA

    def getYearsNotLFA(self):
        return self.yearsNotLFA

    def getSuperDomain(self):
        return self.superDomain

    def getEvents(self):
        return self.events

    def getNumEvents(self):
        return self.numEvents

    def setDomain(self, input):
        self.domain = input

    def appendSuperDomain(self, input):
        self.superDomain.append(input)

    def appendDomain(self, input):
        self.domain.append(input)

    def appendEvents(self, input):
        self.events.append(input)

    def toString(self):
        string = ""
        string += self.email + ", " + self.name + " is in grade "
        + str(self.grade)
        string += ", has previously taken: "
        if len(self.prevCourses) != 0:
            for elem in self.prevCourses:
                string += elem.getName() + ", "
            string = string[:-2]
        else:
            string += "nothing"
        string += " and is currently taking: "
        if len(self.currentCourses) != 0:
            for elem in self.currentCourses:
                string += elem.getName() + ", "
            string = string[:-2]
        else:
            string += "nothing"
        string += " and has done " + str(self.extracurriculars) + " ecs"
        string += ". They have commitment level " + str(self.commitment)
        + " and have been in scioly for " + str(self.yearsLFA)
        + " years at LFA and " + str(self.yearsNotLFA) + " years not at LFA"
        string += ". They want to be in " + str(self.numEvents)
        + " events, and their top choices are: "
        for elem in self.choices:
            string += str(elem) + ", "
        return string[:-2]

    def removeDomain(self, input):
        self.domain.remove(input)


class Course():
    def __init__(self, name, weight, subjects, id):
        self.name = name
        self.weight = weight
        self.subjects = subjects
        self.id = id

    def getId(self):
        return self.id

    def getName(self):
        return self.name

    def getSubjects(self):
        return self.subjects

    def getWeight(self):
        return self.weight


class ExtraCurricular():
    def __init__(self, name, id):
        self.name = name
        self.id = id

    def getId(self):
        return self.id

    def getName(self):
        return self.name


class Event():
    def __init__(self, name, numPeople, block, subjects, id):
        self.name = name
        self.numTruePeople = numPeople
        self.block = block
        self.subjects = subjects
        self.id = id
        self.superDomain = list()
        self.domain = list()
        self.people = list()
        self.numPeople = numPeople

    def getId(self):
        return self.id

    def getNumPeople(self):
        return self.numPeople

    def getName(self):
        return self.name

    def getBlock(self):
        return self.block

    def getDomain(self):
        return self.domain

    def getSubjects(self):
        return self.subjects

    def getNumTruePeople(self):
        return self.numTruePeople

    def getSuperDomain(self):
        return self.superDomain

    def getPeople(self):
        return self.people

    def setNumPeople(self, input):
        self.numPeople = input

    def setPeople(self, input):
        self.people = input

    def setDomain(self, input):
        self.domain = input

    def appendPeople(self, input):
        self.people.append(input)

    def appendSuperDomain(self, input):
        self.superDomain.append(input)

    def appendDomain(self, input):
        self.domain.append(input)

    def removeDomain(self, input):
        self.domain.remove(input)

    def reverseDomain(self):
        self.domain.reverse()
