import chess
import chess.engine
import time

# Chemin vers l'exécutable Stockfish sur votre système
# (Modifiez ce chemin selon votre installation, ex: "/usr/games/stockfish" ou "C:/path/to/stockfish.exe")
STOCKFISH_PATH = "stockfish" 

class ChessRobotAI:
    def __init__(self, difficulty="easy"):
        """
        Initialise le cerveau du robot d'échecs.
        :param difficulty: "easy", "intermediate" ou "hard"
        """
        self.board = chess.Board()
        self.difficulty = difficulty
        
        try:
            self.engine = chess.engine.SimpleEngine.spawn_uci(STOCKFISH_PATH)
        except Exception as e:
            print(f"Erreur : Impossible de lancer Stockfish. Vérifiez le chemin. ({e})")
            exit(1)
            
        self.configure_difficulty()

    def configure_difficulty(self):
        """Configure les paramètres de Stockfish selon le mode choisi."""
        if self.difficulty == "easy":
            # Mode Facile : Stockfish débutant (Skill Level 3 sur 20)
            self.engine.configure({"Skill Level": 3})
            self.limit = chess.engine.Limit(time=0.2)
            print("🤖 Mode Facile activé (Niveau 3 - Idéal pour débuter).")
            
        elif self.difficulty == "intermediate":
            # Mode Intermédiaire : Niveau modéré (Skill Level 12)
            self.engine.configure({"Skill Level": 12})
            self.limit = chess.engine.Limit(time=0.5)
            print("🤖 Mode Intermédiaire activé (Niveau 12 - Erreurs tactiques possibles).")
        
        elif self.difficulty == "hard":
            # Mode Difficile : Pleine puissance (Skill Level 20, calcul profond)
            self.engine.configure({"Skill Level": 20})
            self.limit = chess.engine.Limit(time=2.0)
            print("🤖 Mode Difficile activé (Niveau MAX - Ne pardonne rien).")
        else:
            raise ValueError("Mode inconnu. Choisissez 'easy', 'intermediate' ou 'hard'.")

    def play_robot_turn(self):
        """Calcule et joue le meilleur coup pour le robot."""
        if self.board.is_game_over():
            return None
        
        print("Le robot réfléchit...")
        result = self.engine.play(self.board, self.limit)
        move = result.move
        
        # Applique le coup sur l'échiquier virtuel
        self.board.push(move)
        return move

    def play_human_turn(self, move_uci):
        """
        Joue le coup du joueur humain (ex: "e2e4").
        Vérifie si le coup est légal.
        """
        try:
            move = chess.Move.from_uci(move_uci)
            if move in self.board.legal_moves:
                self.board.push(move)
                return True
            else:
                print("Coup illégal ! Réessayez.")
                return False
        except ValueError:
            print("Format de coup invalide (utilisez le format UCI ex: e2e4).")
            return False

    def close(self):
        """Ferme proprement le moteur Stockfish."""
        self.engine.quit()


# --- Exemple de boucle de jeu en console ---
if __name__ == "__main__":
    print("=== BIENVENUE DANS LE ROBOT D'ÉCHECS ===")
    print("Choisissez le mode de difficulté :")
    print("1. Facile")
    print("2. Intermédiaire")
    print("3. Difficile")
    
    choice = input("Votre choix (1, 2 ou 3) : ").strip()
    
    if choice == "1":
        diff_mode = "easy"
    elif choice == "3":
        diff_mode = "hard"
    else:
        diff_mode = "intermediate"
        
    robot = ChessRobotAI(difficulty=diff_mode)
    
    print("\nL'échiquier est prêt. Les Blancs sont aux échecs.")
    print("Entrez vos coups au format UCI (ex: 'e2e4' pour avancer le pion e).")
    print("Tapez 'exit' pour quitter.\n")

    try:
        while not robot.board.is_game_over():
            print("\n" + str(robot.board))
            print("-" * 30)
            
            # Tour du joueur humain (ex: les Blancs)
            human_move = input("Votre coup : ")
            if human_move.lower() == 'exit':
                break
                
            if not robot.play_human_turn(human_move):
                continue
                
            if robot.board.is_game_over():
                break
                
            # Tour du robot (ex: les Noirs)
            robot_move = robot.play_robot_turn()
            print(f"Le robot a joué : {robot_move}")

        print("\nPartie terminée !")
        print("Résultat :", robot.board.result())

    finally:
        robot.close()
