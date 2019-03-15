import numpy as np
import pandas as pd
import os
import glob
import ast
import csv
import time
import interruptionFinder
import openpyxl as openpyxl

'''
    Reads a map from a given input file
'''
def read_map(input_file):
    with open(input_file, 'rt') as infile:
        grid1 = np.array([list(line.strip()) for line in infile.readlines()])
    print('Grid shape', grid1.shape)

    grid1[grid1 == '@'] = 1  # object on the map
    grid1[grid1 == 'T'] = 1  # object on the map
    grid1[grid1 == '.'] = 0  # free on map

    return np.array(grid1.astype(np.int))


'''
    Read the agents original plan, i.e., their routes
'''
def read_routes_from_file(input_file):
    main_routes = []

    # reading csv file
    with open(input_file, 'rt') as csvfile:
        # creating a csv reader object
        csvreader = csv.reader(csvfile)
        # extracting each data row one by one
        for row in csvreader:
            tmp_route = []
            for y in range(0, len(row)):
                if row[y]:
                    tmp_route.append(ast.literal_eval(row[y]))
            main_routes.append(tmp_route)
    return main_routes

def main():
    # Experiment parameters
    k=3

    # Read the map
    grid = read_map('room1.txt')

    # For every routes file, start an experiment
    path = 'Data\\'
    extension = 'csv'
    os.chdir(path)
    files = [i for i in glob.glob('*.{}'.format(extension))]

    writer = pd.ExcelWriter('Results.xlsx', engine='openpyxl')
    counter = 0

    for file in files:
        print(file)
        counter = counter + 1
        total_expanded_nodes = 0
        org_total_g = 0
        new_total_g = 0


        original_routes = read_routes_from_file(file)

        for x in range(0, len(original_routes)):
            org_total_g = org_total_g + len(original_routes[x])-1


        solution = []

        start_time = time.time()

        # Run the search for interrupts process
        search_algorithm = interruptionFinder.InterruptionFinder()
        solution, route, total_expanded_nodes = search_algorithm.search_for_interrupt_plan(grid,k,original_routes)

        # Output search results
        elapsed_time = time.time() - start_time

        print(file)
        print(counter)
        print('Total runtime: '+ str(elapsed_time))
        total_routes_cost = sum([len(route)-1 for route in solution[0].route])
        print('Total routes cumulative sum: '+ str(total_routes_cost))
        print('Total expanded nodes: '+ str(total_expanded_nodes))
        print('Number of interruption for best solution: '+str(k - solution[-1].k))
        new_total_g = 0


        for x in range(0, len(route)):
            #print('**** Agent ', x, '****')
            start = route[x][0][0]
            goal = route[x][-1][0]
            first_time_goal = 1
            colors = ['r', 'purple', 'b', 'c', 'm', 'y', 'k', 'w']
            ##############################################################################
            # plot the path
            ##############################################################################

            # extract x and y coordinates from route list
            x_coords = []
            y_coords = []
            for y in range(0, len(solution)):

                x1 = solution[y].pos[x][0]
                y1 = solution[y].pos[x][1]

                if x1 == (route[x][-1][0][0]) and y1 == (route[x][-1][0][1]):
                    if first_time_goal == 0:
                        continue
                    else:
                        first_time_goal = 0
                else:
                    new_total_g = new_total_g + 1

                x_coords.append(x1)
                y_coords.append(y1)

            # plot path
            #ax.scatter(start[1], start[0], marker="*", color="black", s=50)
            #ax.scatter(goal[1], goal[0], marker="*", color="y", s=50)
            #if x <= len(colors):
            #    ax.plot(y_coords, x_coords, color=colors[x], label=x)
            #else:
            #    ax.plot(y_coords, x_coords, color=colors[len(colors)], label=x)

        print('Original g_score is - ', org_total_g)
        print('New g_score is - ', new_total_g)
        no_of_interrupt = k - solution[-1].k
        df_res = df_res.append({'dataset_name': file,
                                'Runtime': elapsed_time,
                                'org_g_score': org_total_g,
                                'Total_expanded_nodes': total_expanded_nodes,
                                'Number_of_interruption': no_of_interrupt,
                                'New_g_score': new_total_g}, ignore_index=True)

        if os.path.exists('Results.xlsx'):
            book = openpyxl.load_workbook('Results.xlsx')
            writer.book = book
        # Convert the dataframe to an XlsxWriter Excel object.
        df_res.to_excel(writer, sheet_name=file, index=False)
        # Close the Pandas Excel writer and output the Excel file.
        writer.save()

        # ---For ploting the map DO:---

        #minor_ticks = np.arange(0, 261, 1)
        #ax.set_xticks(minor_ticks, minor=True)
        #ax.set_yticks(minor_ticks, minor=True)
        #ax.grid(which='both')
        #plt.show()

    writer.close()



if __name__ == "__main__":
    main()