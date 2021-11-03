import itertools
import random
import termcolor

class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    # Returns the set of all cells in self.cells known to be mines.
    def known_mines(self):
        if len(self.cells) == self.count:
            return self.cells
        return set()

    # Returns the set of all cells in self.cells known to be safe.
    def known_safes(self):
        if not self.count:
            return self.cells
        return set()

    # Updates internal knowledge representation given the fact that
    # a cell is known to be a mine.
    def mark_mine(self, cell):
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    # Updates internal knowledge representation given the fact that
    # a cell is known to be safe.
    def mark_safe(self, cell):
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    # Marks a cell as a mine, and updates all knowledge
    # to mark that cell as a mine as well.
    def mark_mine(self, cell):
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    # Marks a cell as safe, and updates all knowledge
    # to mark that cell as safe as well.
    def mark_safe(self, cell):
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_current_sentence_move(self, cell, count):
        #print("I add the sentence for", cell);
        neighbors = set()
        if cell not in self.safes:
            neighbors.add(cell)
        for i in range(cell[0]-1, cell[0]+2):
            for j in range(cell[1]-1, cell[1]+2):
                if 0<=i<self.height and 0<=j<self.width and (i,j) != cell:
                    if (i, j) in self.mines:
                        count -=1
                        continue
                    if (i, j) not in self.safes:
                        neighbors.add((i, j))
        sentence = Sentence(neighbors, count)
        self.knowledge.append(sentence)
        #termcolor.cprint("I am adding the sentence:", 'yellow')
        #termcolor.cprint(sentence, 'yellow')

    def subset_rule(self):

        def sub(sentence1, sentence2):
            new = Sentence(sentence1.cells - sentence2.cells, sentence1.count - sentence2.count)
            self.knowledge.remove(sentence1)
            self.knowledge.append(new)
            #termcolor.cprint("I am removing the sentence:", 'yellow')
            #termcolor.cprint(sentence1, 'yellow')
            #termcolor.cprint("I am adding the sentence:", 'yellow')
            #termcolor.cprint(new, 'yellow')


        while True:
            #print("In the while")
            found_new = False
            for sentence1 in self.knowledge:
                if found_new:
                    break
                for sentence2 in self.knowledge:
                    if found_new:
                        break
                    if sentence1 != sentence2 and sentence1.cells and sentence2.cells:
                        if sentence1.cells.issubset(sentence2.cells):
                            found_new = True
                            #termcolor.cprint("---", "blue")
                            #termcolor.cprint(sentence1.cells, "blue")
                            #termcolor.cprint(sentence2.cells, "blue")
                            #termcolor.cprint("---", "blue")
                            sub(sentence2, sentence1)
                        elif sentence2.cells.issubset(sentence1.cells):
                            found_new = True
                            #termcolor.cprint("---", "blue")
                            #termcolor.cprint(sentence1.cells, "blue")
                            #termcolor.cprint(sentence2.cells, "blue")
                            #termcolor.cprint("---", "blue")
                            sub(sentence1, sentence2)
            if not found_new:
                break

    def mark_new_cells(self):
        for sentence in self.knowledge:
            if not sentence.cells:
                self.knowledge.remove(sentence)
                break
            #print("I examine sentence:", end=' ')
            #print(sentence)
            for cell in sentence.cells.copy():
                #print("I examine cell:", end=' ')
                #print(cell)
                if cell in sentence.known_mines():
                    #print("It is mine for sure")
                    self.mark_mine(cell)
                elif cell in sentence.known_safes():
                    #print("It is safe for sure")
                    self.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        #termcolor.cprint("-----------I am adding knowledge-----------------------", "blue")
        #termcolor.cprint("Step (1) and (2)", "blue")
        self.moves_made.add(cell)
        self.mark_safe(cell)
        #self.print_state()


        # ----- (3) add a new sentence -----
        #termcolor.cprint("\t\t\tStep (3)", "blue")
        self.add_current_sentence_move(cell, count)
        #self.print_state()
        

        # ----- (4) mark additional cells -----
        #termcolor.cprint("\t\t\tStep (4)", "blue")
        self.mark_new_cells()
        #self.print_state()

        # ----------------------------------

        # ----- (5) add new sentences using subset rule -----
        #termcolor.cprint("\t\t\tStep (5)", "blue")
        self.subset_rule()
        #self.print_state()
        # ----- (6) i mark new cells again
        self.mark_new_cells()
        # ----------------------------------
        #termcolor.cprint("I added the knowledge", "blue")
        #self.print_state()


    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """

        #self.print_state()

        for cell in self.safes - self.moves_made:
            #termcolor.cprint("I am making a safe move at one of the", 'green')
            #termcolor.cprint(self.safes, 'green')
            return cell
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        for i in range(self.width):
            for j in range(self.height):
                cell = (i, j)
                if cell not in set.union(self.mines, self.moves_made):
                    #termcolor.cprint("I am making a random move at the", 'yellow')
                    #termcolor.cprint(cell, 'yellow')
                    return cell
        return None

    def print_state(self):
        termcolor.cprint("Current state:", "white")
        print("Played:", end = ' ')
        termcolor.cprint(self.moves_made, "red")
        print("Safes:", end = ' ')
        termcolor.cprint(self.safes, "red")
        print("Safes left:", end = ' ')
        termcolor.cprint(self.safes - self.moves_made, "red")
        print("Mines", end = ' ')
        termcolor.cprint(self.mines, "red")
        self.print_knowledge()

    def print_knowledge(self):
        termcolor.cprint("Knowledge:", "green")
        for sentence in self.knowledge:
            #termcolor.cprint(sentence, "green")
            pass