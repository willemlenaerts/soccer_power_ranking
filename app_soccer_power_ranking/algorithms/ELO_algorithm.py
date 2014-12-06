__author__ = 'Exergos'
__project__ = 'SPI_JupilerProLeague'

########################################################################################################################
########################################################################################################################

#########################
# What does this file do?
#########################

# This file calculates the ELO Rating for every team of the Jupiler Pro League

# Python 3.3 as Interpreter
# sporza to import sporza data
# Numpy for mathematical use

######################
# What does it return?
######################

# Returns a list of 2 items
# [0]:  List of 2 things
# [0][1]: Team names of all teams in Jupiler Pro League
#       [0][2]: Array of size (number of teams x 3)
#               [0][2][:,0]: SPI
#               [0][2][:,1]: Off Rating
#               [0][2][:,2]: Def Rating

# [1]:  Array of size ((games played + games not played) x 8)
#       [1][:,0]: Home Team (As a number, alphabetically as in [0]
#       [1][:,1]: Away Team (As a number, alphabetically as in [0]
#       [1][:,2]: Home Team Goals
#       [1][:,3]: Away Team Goals
#       [1][:,4]: Probability of Home Win
#       [1][:,5]: Probability of Tie
#       [1][:,6]: Probability of Away Win
#       [1][:,7]: Game already played? (1 = yes, 0 = no)

########################################################################################################################
########################################################################################################################
def elo():
    import numpy as np
    from app_soccer_power_ranking.algorithms.sporza import get_data
    # import sporza

    # Import Scraped Data
    data = get_data()
    # [0]:  Team names of all teams in Jupiler Pro League
    # [1]:  Array of size (games played x 4)
    #       [1][:,0]: Home Team (As a number, alphabetically as in [0]
    #       [1][:,1]: Away Team (As a number, alphabetically as in [0]
    #       [1][:,2]: Home Team Goals
    #       [1][:,3]: Away Team Goals

    # Define some parameters that will help with reading the code
    number_of_teams = len(data[0])
    total_games = number_of_teams * (number_of_teams - 1)
    games_played = len(data[1])
    games_not_played = total_games - games_played

    # Calculate ELO using ELO Formula
    # ELO parameters
    elo_start = 1500
    K = 50
    home_field_advantage = 84 # http://clubelo.com/HFA/ for belgium

    # Every team starts off with 1500 before season
    # Calculate through season

    elo_rating_after_game = np.zeros((games_played,number_of_teams))

    for i in range(games_played):
        # Calculate W_home, W_away and G parameter for game
        if data[1][i,2] > data[1][i,3]: # Home Win
            W_home = 1
            W_away = 0
        if data[1][i,2] == data[1][i,3]: # Draw
            W_home = 0.5
            W_away = 0.5
        if data[1][i,2] < data[1][i,3]: # Away Win
            W_home = 0
            W_away = 1

        # G
        if data[1][i,2] == data[1][i,3] or abs(data[1][i,2] - data[1][i,3]) == 1: # Draw or 1 goal difference
            G = 1
        else:
            if abs(data[1][i,2] - data[1][i,3]) == 2: # 2 goals difference
                G = 3/2
            else: # 3 or more goals difference
                G = (11 + abs(data[1][i,2] - data[1][i,3]))/8

        # Calculate ELO rating AFTER game
        if i == 0: # First game of the season
            # Home Team new ELO rating after game
            W_home_e = 1/(10**(-home_field_advantage/400)+1)
            elo_rating_after_game[i,data[1][i,0]] = elo_start + K*G*(W_home-W_home_e)

            # Away Team new ELO rating after game
            W_away_e = 1/(10**(home_field_advantage/400)+1)
            elo_rating_after_game[i,data[1][i,1]] = elo_start + K*G*(W_away-W_away_e)
        else:
            # Home Team new ELO rating after game
            W_home_e = 1/(10**(-(elo_rating_after_game[i-1,data[1][i,0]]+home_field_advantage-elo_rating_after_game[i-1,data[1][i,1]])/400)+1)
            elo_rating_after_game[i,data[1][i,0]] = elo_rating_after_game[i-1,data[1][i,0]] + K*G*(W_home-W_home_e)

            # Away Team new ELO rating after game
            W_away_e = 1/(10**(-(elo_rating_after_game[i-1,data[1][i,1]]-home_field_advantage-elo_rating_after_game[i-1,data[1][i,0]])/400)+1)
            elo_rating_after_game[i,data[1][i,1]] = elo_rating_after_game[i-1,data[1][i,1]] + K*G*(W_away-W_away_e)

        # For every team that didn't play, copy old elo into new spot
        for j in range(number_of_teams):
            if elo_rating_after_game[i,j] == 0:
                if i == 0:
                    elo_rating_after_game[i,j] = elo_start
                else:
                    elo_rating_after_game[i,j] = elo_rating_after_game[i-1,j]


    # Now calculate Win/Loss/Draw expectancy for games not played yet
    # First estimate expected goals (Proba is W_home_e)
    # Home Team
    if W_home_e < 0.5:
        home_goals = 0.2 + 1.1*np.sqrt(W_home_e/0.5)
    else:
        home_goals = 1.69 / (1.12*np.sqrt(2 - W_home_e/0.5)+0.18)

    # Goals for the Away team:
    if W_home_e < 0.8:
        away_goals = -0.96 + 1/(0.1+0.44*np.sqrt((W_home_e+0.1)/0.9))
    else:
        away_goals = 0.72*np.sqrt((1 - W_home_e)/0.3)+0.3

    # Now use poisson distribution to determine for each team the chance it scores x goals

    # Combine these for both teams to calculate Win/Loss/Draw expectancy

    return list([data[0], elo_rating_after_game])


    #     # Calculate SPI using ESPN algorithm
    # # Step 1: Assume off_rating & def_rating for every team
    # # Based on goals scored in played matches
    # goals = np.zeros((number_of_teams, 3))
    # for i in range(number_of_teams):
    #     for j in range(games_played):
    #         if data[1][j, 0] == i:  # Home team
    #             goals[i, 0] = goals[i, 0] + data[1][j, 2]
    #             goals[i, 1] = goals[i, 1] + data[1][j, 3]
    #             goals[i, 2] = goals[i, 2] + 1
    #         if data[1][j, 1] == i:  # Away team
    #             goals[i, 0] = goals[i, 0] + data[1][j, 3]
    #             goals[i, 1] = goals[i, 1] + data[1][j, 2]
    #             goals[i, 2] = goals[i, 2] + 1
    #
    # off_rating = np.matrix(np.divide(goals[:, 0], goals[:, 2])).transpose()
    # def_rating = np.matrix(np.divide(goals[:, 1], goals[:, 2])).transpose()
    # # Calculate starting values (to make sure iterative process is converging)
    # # Initialize data & parameters
    # avg_base = 1.37  # Average number of goals scored per team per game in competition (based on historic data)
    # # Use lists for ags/aga because exact size is unknown beforehand
    # ags = [[] for x in range(number_of_teams)]
    # aga = [[] for x in range(number_of_teams)]
    #
    # for i in range(games_played):  # For every game
    #     for k in range(number_of_teams):  # Check home and away team
    #         if data[1][i, 0] == k:  # Team was home team for this game
    #             home_team = k
    #         if data[1][i, 1] == k:  # Team was away team for this game
    #             away_team = k
    #     # Home team ags & aga calculation
    #     ags_dummy = ((data[1][i, 2] - def_rating[away_team, 0]) / max(0.25,
    #                                                                   def_rating[away_team, 0] * 0.424 + 0.548)) * (
    #                     avg_base * 0.424 + 0.548) + avg_base
    #     aga_dummy = ((data[1][i, 3] - off_rating[away_team, 0]) / max(0.25,
    #                                                                   off_rating[away_team, 0] * 0.424 + 0.548)) * (
    #                     avg_base * 0.424 + 0.548) + avg_base
    #     ags[home_team].append(ags_dummy)
    #     aga[home_team].append(aga_dummy)
    #
    #     # Away team ags & aga calculation
    #     ags_dummy = ((data[1][i, 3] - def_rating[home_team, 0]) / max(0.25,
    #                                                                   def_rating[home_team, 0] * 0.424 + 0.548)) * (
    #                     avg_base * 0.424 + 0.548) + avg_base
    #     aga_dummy = ((data[1][i, 2] - off_rating[home_team, 0]) / max(0.25,
    #                                                                   off_rating[home_team, 0] * 0.424 + 0.548)) * (
    #                     avg_base * 0.424 + 0.548) + avg_base
    #     ags[away_team].append(ags_dummy)
    #     aga[away_team].append(aga_dummy)
    #
    # # Test if off and def ratings are converging (least squares test)
    # for i in range(number_of_teams):
    #     off_rating[i, 0] = sum(ags[i]) / float(len(ags[i]))
    #     def_rating[i, 0] = sum(aga[i]) / float(len(aga[i]))
    #
    # # Step 2: Calculate Adjusted Goals Scored (AGS) and Adjusted Goals Allowed (AGA) for every game & Iterate to find off and def rating
    # error = 0.5
    # iter_test = list([error + 1])
    # iter_test2 = np.zeros((games_played, 30))
    # iter = 0
    # while iter_test[iter] > error and iter < 30:
    #
    #     # Initialize data & parameters
    #     avg_base = 1.37  # Average number of goals scored per team per game in competition (based on historic data)
    #     # Use lists for ags/aga because exact size is unknown beforehand
    #     ags = [[] for x in range(number_of_teams)]
    #     aga = [[] for x in range(number_of_teams)]
    #
    #     for i in range(games_played):  # For every game
    #         for k in range(number_of_teams):  # Check home and away team
    #             if data[1][i, 0] == k:  # Team was home team for this game
    #                 home_team = k
    #             if data[1][i, 1] == k:  # Team was away team for this game
    #                 away_team = k
    #         # Home team ags & aga calculation
    #         ags_dummy = ((data[1][i, 2] - def_rating[away_team, iter]) / max(0.25, def_rating[
    #             away_team, iter] * 0.424 + 0.548)) * (avg_base * 0.424 + 0.548) + avg_base
    #         aga_dummy = ((data[1][i, 3] - off_rating[away_team, iter]) / max(0.25, off_rating[
    #             away_team, iter] * 0.424 + 0.548)) * (avg_base * 0.424 + 0.548) + avg_base
    #         ags[home_team].append(ags_dummy)
    #         aga[home_team].append(aga_dummy)
    #
    #         iter_test2[i, iter] = max(0.25, def_rating[away_team, iter] * 0.424 + 0.548)
    #
    #         # Away team ags & aga calculation
    #         ags_dummy = ((data[1][i, 3] - def_rating[home_team, iter]) / max(0.25, def_rating[
    #             home_team, iter] * 0.424 + 0.548)) * (avg_base * 0.424 + 0.548) + avg_base
    #         aga_dummy = ((data[1][i, 2] - off_rating[home_team, iter]) / max(0.25, off_rating[
    #             home_team, iter] * 0.424 + 0.548)) * (avg_base * 0.424 + 0.548) + avg_base
    #         ags[away_team].append(ags_dummy)
    #         aga[away_team].append(aga_dummy)
    #
    #     # Test if off and def ratings are converging (least squares test)
    #     iter = iter + 1
    #     off_rating = np.c_[off_rating, np.zeros(number_of_teams)]
    #     def_rating = np.c_[def_rating, np.zeros(number_of_teams)]
    #     for i in range(number_of_teams):
    #         off_rating[i, iter] = sum(ags[i]) / float(len(ags[i]))
    #         def_rating[i, iter] = sum(aga[i]) / float(len(aga[i]))
    #
    #     # iter_test = sum(np.absolute(off_rating[:,iter-1] - off_rating[:, iter]))
    #     iter_test.append(sum(np.sqrt(np.square(off_rating[:, iter - 1] - off_rating[:, iter]))))
    #
    #     # EXTRA TEST TO ENSURE CONVERGENCE
    #     if (iter_test[iter] - iter_test[iter - 1]) < error and iter_test[iter] > error:
    #         off_rating[:, iter] = (off_rating[:, iter] + off_rating[:, iter - 1]) / 2
    #         def_rating[:, iter] = (def_rating[:, iter] + def_rating[:, iter - 1]) / 2
    #
    # # Step 3: Calculate SPI (Using "A Model Based Ranking System for Soccer Teams" by Wang/Vandebroek
    # # First compose OFF & DEF rating into strength factor for every game
    # # Strength home team = off_rating(home_team)*def_rating(away_team)
    # # Strength away team = off_rating(away_team)*def_rating(home_team)
    # # Game result = 1 if home victory, 2 if tie, 3 if away victory
    # # Home factor (H): to be determined
    # # Tie factor (K): to be determined
    #
    # # FOR NOW, ASSUME H = 2.08 and K = 0.905 (see Wang/Vandebroek)
    # H = 2.08
    # K = 0.905
    #
    # # Calculate probabilities for all possible matches in Jupiler Pro League
    # # Extend data[1] with games not yet played (rows)
    # data[1] = np.r_[data[1], np.zeros((games_not_played, data[1].shape[1]))]
    # count = 0
    # for i in range(number_of_teams):  # Home Team
    #     for j in range(number_of_teams):  # Away Team
    #         played = 0
    #         if (i is not j):
    #             for k in range(games_played):
    #                 if data[1][k, 0] == i and data[1][k, 1] == j:
    #                     played = 1
    #             if played == 0:
    #                 data[1][games_played + count, 0] = i
    #                 data[1][games_played + count, 1] = j
    #                 count = count + 1
    #
    # # Extend data[1] with extra columns
    # data[1] = np.c_[data[1], np.zeros(
    #     (total_games, 4))]  # 4 extra data columns (prob home win, prob tie, prob away win, game already played)
    #
    # # Add game already played data
    # for i in range(total_games):
    #     data[1][0:games_played, (data[1].shape[1] - 1)] = 1
    #
    # # Calculate probabilities
    # for i in range(total_games):
    #     # Probability for Home Win
    #     data[1][i, 4] = H * off_rating[data[1][i, 0].astype(int), iter] * def_rating[
    #         data[1][i, 1].astype(int), iter] / (
    #                         H * off_rating[data[1][i, 0].astype(int), iter] * def_rating[data[1][i, 1].astype(int), iter] +
    #                         off_rating[data[1][i, 1].astype(int), iter] * def_rating[
    #                             data[1][i, 0].astype(int), iter] + K * np.sqrt(
    #                             H * off_rating[data[1][i, 0].astype(int), iter] * def_rating[
    #                                 data[1][i, 1].astype(int), iter] * off_rating[data[1][i, 1].astype(int), iter] *
    #                             def_rating[data[1][i, 0], iter]))
    #     # Probability for Tie
    #     data[1][i, 5] = K * np.sqrt(
    #         H * off_rating[data[1][i, 0].astype(int), iter] * def_rating[data[1][i, 1].astype(int), iter] * off_rating[
    #             data[1][i, 1].astype(int), iter] * def_rating[data[1][i, 0].astype(int), iter]) / (
    #                         H * off_rating[data[1][i, 0].astype(int), iter] * def_rating[data[1][i, 1].astype(int), iter] +
    #                         off_rating[data[1][i, 1].astype(int), iter] * def_rating[
    #                             data[1][i, 0].astype(int), iter] + K * np.sqrt(
    #                             H * off_rating[data[1][i, 0].astype(int), iter] * def_rating[
    #                                 data[1][i, 1].astype(int), iter] * off_rating[data[1][i, 1].astype(int), iter] *
    #                             def_rating[data[1][i, 0].astype(int), iter]))
    #     # Probability for Away Win
    #     data[1][i, 6] = off_rating[data[1][i, 1].astype(int), iter] * def_rating[data[1][i, 0].astype(int), iter] / (
    #         H * off_rating[data[1][i, 0].astype(int), iter] * def_rating[data[1][i, 1].astype(int), iter] + off_rating[
    #             data[1][i, 1].astype(int), iter] * def_rating[data[1][i, 0].astype(int), iter] + K * np.sqrt(
    #             H * off_rating[data[1][i, 0].astype(int), iter] * def_rating[data[1][i, 1].astype(int), iter] * off_rating[
    #                 data[1][i, 1].astype(int), iter] * def_rating[data[1][i, 0].astype(int), iter]))
    #
    # # Calculate SPI
    # # SPI is always calculated assuming nog games have been played (i.e. a round robin between all teams)
    # SPI = np.matrix(np.zeros(number_of_teams)).transpose()
    # for i in range(number_of_teams):
    #     for j in range(total_games):
    #         if data[1][j, 0] == i:  # Home Team
    #             SPI[i, 0] = SPI[i, 0] + (3 * data[1][j, 4] + 1 * data[1][j, 5] + 0 * data[1][j, 6]) / 3
    #         if data[1][j, 1] == i:  # Away Team
    #             SPI[i, 0] = SPI[i, 0] + (0 * data[1][j, 4] + 1 * data[1][j, 5] + 3 * data[1][j, 6]) / 3
    #     SPI[i, 0] = SPI[i, 0] / (2 * total_games / number_of_teams)
    #
    # return list([[data[0], np.concatenate((SPI, off_rating[:, iter], def_rating[:, iter]), axis=1)], data[1]])