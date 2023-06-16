import os
import sys
import random
import numpy as np
from PIL import Image, ImageDraw, ImageOps
from copy import deepcopy

TARGET_IMG = sys.argv[1]
GENOME_SIZE = int(sys.argv[2])
POPULATION_SIZE = int(sys.argv[3])
GENERATIONS = int(sys.argv[4])

def tint_image(src: Image, color: tuple=(255, 255, 255)):
    src.load()
    r, g, b, alpha = src.split()
    gray = ImageOps.grayscale(src)
    result = ImageOps.colorize(gray, (0, 0, 0, 0), color)
    result.putalpha(alpha)
    return result

def renderBanner(genome):
    banner = Image.new("RGBA", (400,780), pallete[0][1])
    for i in range(len(genome["layers"])):
        p = Image.open(os.path.join(os.path.dirname(__file__), "img/pattern_" + str(genome["layers"][i]).zfill(2) + ".png"))
        pattern = tint_image(p, pallete[genome["colours"][i]][1])
        pattern.convert("RGBA")
        banner = Image.alpha_composite(banner, pattern)
    return banner

pallete = [
    ["Black", (25, 25, 25)], #191919 0
    ["Gray", (76, 76, 76)], #4c4c4c 1
    ["Light Gray", (153, 153, 153)], #999999 2
    ["White", (242, 242, 242)], #f2f2f2 3
    ["Pink", (242, 127, 165)], #f27fa5 4
    ["Magenta", (178, 76, 216)], #b24cd8 5
    ["Purple", (127, 63, 178)], #7f3fb2 6
    ["Blue", (51, 76, 178)], #334cb2 7
    ["Cyan", (76, 127, 153)], #4c7f99 8
    ["Light Blue", (102, 153, 216)], #4c7f99 9
    ["Green", (102, 127, 51)], #667f33 10
    ["Lime", (127, 204, 25)], #7fcc19 11
    ["Yellow", (229, 229, 51)], #e5e533 12
    ["Orange", (216, 127, 51)], #d87f33 13
    ["Brown", (102, 76, 51)], #664c33 14
    ["Red", (153, 51, 51)] #993333 15
]

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
    random.shuffle(newGenome["layers"])
    random.shuffle(newGenome["colours"])
    return newGenome


def mutate(genome):
    nucleotideToMutate = random.randint(0,genome["size"]-1)
    mutationType = random.choice(["layer","colour","both","swapBoth","shuffle"])
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
        return shuffleGenome(genome)

def randomGenomeOfSize(size):
    layers = list(map(lambda i: random.randint(1, 38),range(size)))
    colours = list(map(lambda i: random.randint(0, 15),layers ))
    return {"layers": layers, "colours": colours, "size":size, "fitness":None, "render":None}

def evaluateGenome(genome,target):
    if genome["fitness"] is not None:
        return genome
    genomeCopy = deepcopy(genome)
    genomeCopy["render"] = np.asarray(renderBanner(genome))[:,:,:3]
    genomeCopy["fitness"] = np.sum(np.absolute(genomeCopy["render"] - target)) + genomeCopy["size"]*100
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
        print(str(i) + " best performing fitness: " + str(population[0]["fitness"]) +" size: "+str(population[0]["size"]))
        tmpImg = Image.fromarray(population[0]["render"])
        tmpImg.save(os.path.join(os.path.dirname(__file__), "outputs/output"+str(outcount)+".png"))
        lastBest = population[0]
        outcount+=1
    #keep only best in population
    population = population[:int(len(population)/4)]
    #repopulate using childs of above
    while len(population) < POPULATION_SIZE:
        child = mutate(random.choice(population))#allow childs of childs
        child["fitness"] = None
        population.append(child)
    population = list(map(lambda x: evaluateGenome(x,targetImage), population))

