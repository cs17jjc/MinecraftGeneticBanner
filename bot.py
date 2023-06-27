import os
import sys
import random
import numpy as np
from PIL import Image, ImageDraw, ImageOps
from copy import deepcopy

TARGET_IMG = sys.argv[1]
POPULATION_SIZE = int(sys.argv[2])
GENERATIONS = int(sys.argv[3])
GENOME_SIZE = int(sys.argv[4])

def tint_image(src: Image, color: tuple=(255, 255, 255)):
    src.load()
    r, g, b, alpha = src.split()
    gray = ImageOps.grayscale(src)
    result = ImageOps.colorize(gray, (0, 0, 0, 0), color)
    result.putalpha(alpha)
    return result

def renderBanner(genome):
    banner = Image.new("RGBA", (400,780), pallete[genome["baseColour"]][1])
    for i in range(len(genome["layers"])):
        p = Image.open(os.path.join(os.path.dirname(__file__), "img/pattern_" + str(genome["layers"][i]).zfill(2) + ".png"))
        pattern = tint_image(p, pallete[genome["colours"][i]][1])
        pattern.convert("RGBA")
        banner = Image.alpha_composite(banner, pattern)
    return banner

pallete = [
    ["white", (242, 242, 242)], #f2f2f2 0
    ["orange", (216, 127, 51)], #d87f33 1
    ["magenta", (178, 76, 216)], #b24cd8 2
    ["light_blue", (102, 153, 216)], #4c7f99 3
    ["yellow", (229, 229, 51)], #e5e533 4
    ["lime", (127, 204, 25)], #7fcc19 5
    ["pink", (242, 127, 165)], #f27fa5 6
    ["gray", (76, 76, 76)], #4c4c4c 7
    ["light_gray", (153, 153, 153)], #999999 8
    ["cyan", (76, 127, 153)], #4c7f99 9
    ["purple", (127, 63, 178)], #7f3fb2 10
    ["blue", (51, 76, 178)], #334cb2 11
    ["brown", (102, 76, 51)], #664c33 12
    ["green", (102, 127, 51)], #667f33 13
    ["red", (153, 51, 51)], #993333 14
    ["black", (25, 25, 25)] #191919 15
]
patternNames=["mc","bl","br","tl","tr","hh","bs","ts","vh","ls","cs","rs",
"ms","sc","dls","drs","cr","ld","rud","tt","bt","mr","tts","bts","cbo",
"bo","ss","bri","gra","cre","sku","flo","moj","lud","rd","gru","hhb","vhr"]

def mutateLayer(genome,nucleotide):
    newGenome = deepcopy(genome)
    newGenome["layers"][nucleotide] = random.randint(1, 38)
    return newGenome
def mutateColour(genome,nucleotide):
    newGenome = deepcopy(genome)
    newGenome["colours"][nucleotide] = random.randint(0, 15)
    return newGenome
def mutateLayerAndColour(genome,nucleotide):
    newGenome = deepcopy(genome)
    newGenome["layers"][nucleotide] = random.randint(1, 38)
    newGenome["colours"][nucleotide] = random.randint(0, 15)
    return newGenome

def swapLayerAndColour(genome,nucleotide):
    newGenome = deepcopy(genome)
    neighbour = random.choice([-1,1]) + nucleotide
    if neighbour >= genome["size"]:
        neighbour = 0
    if neighbour < 0:
        neighbour = genome["size"]-1

    neighbourLayer = newGenome["layers"][neighbour]
    neighbourColour = newGenome["colours"][neighbour]
    newGenome["layers"][neighbour] = newGenome["layers"][nucleotide]
    newGenome["colours"][neighbour] = newGenome["colours"][nucleotide]

    newGenome["layers"][nucleotide] = neighbourLayer
    newGenome["colours"][nucleotide] = neighbourColour

    return newGenome
def shiftLeft(genome):
    newGenome = deepcopy(genome)
    newGenome["layers"].append(newGenome["layers"].pop(0))
    newGenome["colours"].append(newGenome["colours"].pop(0))
    return newGenome
def shiftRight(genome):
    newGenome = deepcopy(genome)
    newGenome["layers"].insert(0,newGenome["layers"].pop())
    newGenome["colours"].insert(0,newGenome["colours"].pop())
    return newGenome
def reverseGenome(genome):
    newGenome = deepcopy(genome)
    newGenome["layers"].reverse()
    newGenome["colours"].reverse()
    return newGenome
def shuffleGenome(genome):
    newGenome = deepcopy(genome)
    idx = range(newGenome["size"])
    random.shuffle(idx)
    newGenome["layers"] = newGenome["layers"][idx]
    newGenome["colours"] = newGenome["colours"][idx]
    return newGenome
def baseColour(genome):
    newGenome = deepcopy(genome)
    newGenome["baseColour"] = random.randint(0, 15)
    return newGenome
def grow(genome,nucleotide):
    newGenome = deepcopy(genome)
    newGenome["layers"].insert(nucleotide,random.randint(1, 38))
    newGenome["colours"].insert(nucleotide,random.randint(0, 15))
    newGenome["size"]+=1
    return newGenome
def shrink(genome,nucleotide):
    newGenome = deepcopy(genome)
    if newGenome["size"] == 1:
        return newGenome
    newGenome["layers"].pop(nucleotide)
    newGenome["colours"].pop(nucleotide)
    newGenome["size"]-=1
    return newGenome


def mutate(genome):
    nucleotideToMutate = random.randint(0,genome["size"]-1)
    mutationType = random.choice(["layer","colour","both","swapBoth","shiftLeft","shiftRight","baseColour","reverse","shuffle"])
    #mutationType = random.choice(["layer","colour","both","swapBoth","shiftLeft","shiftRight","baseColour","reverse","shuffle","grow","shrink"])
    if mutationType == "layer":
        return mutateLayer(genome,nucleotideToMutate)
    if mutationType == "colour":
        return mutateColour(genome,nucleotideToMutate)
    if mutationType == "both":
        return mutateLayerAndColour(genome,nucleotideToMutate)
    if mutationType == "swapBoth":
        return swapLayerAndColour(genome,nucleotideToMutate)
    if mutationType == "shiftLeft":
        return shiftLeft(genome)
    if mutationType == "shiftRight":
        return shiftRight(genome)
    if mutationType == "reverse":
        return reverseGenome(genome)
    if mutationType == "shuffle":
        return reverseGenome(genome)
    if mutationType == "baseColour":
        return baseColour(genome)
    if mutationType == "grow":
        return grow(genome,nucleotideToMutate)
    if mutationType == "shrink":
        return shrink(genome,nucleotideToMutate)

def randomGenomeOfSize(size):
    layers = list(map(lambda i: random.randint(1, 38),range(size)))
    colours = list(map(lambda i: random.randint(0, 15),layers ))
    return {"baseColour":0, "layers": layers, "colours": colours, "size":size, "fitness":None, "render":None}

def evaluateGenome(genome,target):
    if genome["fitness"] is not None:
        return genome
    genomeCopy = deepcopy(genome)
    genomeCopy["render"] = np.asarray(renderBanner(genome))[:,:,:3]
    #genomeCopy["fitness"] = np.mean(np.square(genomeCopy["render"] - target)) + genome["size"]*1_000
    genomeCopy["fitness"] = np.mean(np.square(genomeCopy["render"] - target))
    return genomeCopy

def palletiseImage(img):
    pixels = img.load()
    for i in range(img.size[0]):
        for j in range(img.size[1]):
            rgbVal = pixels[i,j][:3]

            currentBestColour = pallete[0][1]
            currentBestDist = np.linalg.norm(np.asarray(currentBestColour)-np.asarray(rgbVal))
            for palleteColour in pallete[1:]:
                rgbDist = np.linalg.norm(np.asarray(palleteColour[1])-np.asarray(rgbVal))
                if rgbDist < currentBestDist:
                    currentBestColour = palleteColour
                    currentBestDist = rgbDist
            pixels[i,j] = currentBestColour[1]

    return img

targetImage = palletiseImage(Image.open(TARGET_IMG)).resize((400, 780))
targetImage = np.asarray(targetImage)[:,:,:3]


population = list(map(lambda i : randomGenomeOfSize(GENOME_SIZE),range(POPULATION_SIZE)))
population = list(map(lambda x: evaluateGenome(x,targetImage), population))
population = sorted(population, key=lambda d: d["fitness"])
lastBest = population[0]
outcount = 0
for i in range(GENERATIONS):
    #order by fitness
    population = sorted(population, key=lambda d: d["fitness"])
    if lastBest["fitness"] > population[0]["fitness"]:
        tmpImg = Image.fromarray(population[0]["render"])
        tmpImg.save(os.path.join(os.path.dirname(__file__), "outputs/output"+str(outcount)+".png"))
        lastBest = population[0]
        outcount+=1
    print("gen: " + str(i) + " best fitness: " + str(population[0]["fitness"]),end='\r')
    #keep only best in population
    population = population[:int(len(population)/2)]
    #repopulate using childs of above
    children = []
    while len(population) + len(children) < POPULATION_SIZE:
        parent = None
        for p in population:
            parent = p
            if random.choice([True, False, False, False]):
                break
        child = mutate(parent)
        child["fitness"] = None
        children.append(child)
    population = list(map(lambda x: evaluateGenome(x,targetImage), population + children))

def finalOutput(genome):
    command = "/give @p " + pallete[genome["baseColour"]][0] +"_banner{BlockEntityTag:{Base:"+str(genome["baseColour"])+",Patterns:["
    bannerAsString = []
    for i in range(genome["size"]):
        bannerAsString.append("{Pattern:"+patternNames[genome["layers"][i]-1]+",Color:"+str(genome["colours"][i])+"}")
    command = command + ','.join(bannerAsString) + "]}} 1"
    print(command)
    if len(command)>256:
        print("COMMAND TO BIG TO PASTE INTO CHAT, USE COMMAND BLOCK")
finalOutput(lastBest)

