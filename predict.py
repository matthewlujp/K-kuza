from PIL import Image


def compute_average_image_color(img):
    width, height = img.size

    r_total = 0
    g_total = 0
    b_total = 0

    count = 0
    for x in range(0, width):
        for y in range(0, height):
            r, g, b = img.getpixel((x, y))
            r_total += r
            g_total += g
            b_total += b
            count += 1

    return (r_total // count, g_total // count, b_total // count)


def judge_maturity():
    img = Image.open('greenmango.jpg')

    average_color = compute_average_image_color(img)

    # print(average_color)
    testrgb = []
    testrgb.append(average_color)
    # print(testrgb)
    # defines RGB boundaries based on statistical means
    yupperboundary = [240, 193, 120]
    ylowerboundary = [200, 153, 58]
    gupperboundary = [121, 160, 100]
    glowerboundary = [81, 120, 60]
    riperegioncheck = []
    riperegioncheck = list(map(lambda pair: max(pair), zip(average_color, yupperboundary)))
    tset = set(riperegioncheck)
    # print(tset)
    yupperboundaryset = set(yupperboundary)
    if (tset.union(yupperboundary) == tset):
        test2 = list(map(lambda pair: min(pair), zip(average_color, ylowerboundary)))
        tset2 = set(test2)
        ylowerboundaryset = set(ylowerboundary)
        if (tset2.union(ylowerboundary) == tset2):
            # print("The Image is of a Ripe Mango")
            return "The Image is of a Ripe Mango"
        else:
            rawregioncheck = []
            rawregioncheck = list(map(lambda pair: max(pair), zip(average_color, gupperboundary)))
            tset = set(rawregioncheck)
            # print(tset)
            gupperbounderyset = set(gupperboundary)
            if(tset.union(gupperboundary) == tset):
                test3 = list(map(lambda pair: min(pair), zip(average_color, glowerboundary)))
                tset3 = set(test3)
                glowerboundaryset = set(glowerboundary)
                if (tset3.union(glowerboundary) == tset3):
                    # print("The Image is a raw Mango")
                    return "The Image is a raw Mango"
    else:
        # print("The image is too noisy")
        return "The image is too noisy"
