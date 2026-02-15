import random
from datetime import datetime, timedelta

def escape_str(val):
    if val is None:
        return "NULL"
    return "'" + str(val).replace("'", "''") + "'"

def generate_sql():
    sql_file = "seed_data.sql"
    print(f"Generating massive SQL seed file: {sql_file}...")
    
    with open(sql_file, "w", encoding="utf-8") as f:
        f.write("BEGIN;\n\n")
        f.write("-- Cleanup existing data\n")
        f.write("TRUNCATE TABLE user_allergens, weight_entries, food_history, diary_meals, diary_days, user_favorite_recipes, user_favorite_restaurants, users, allergens, recipes, restaurants RESTART IDENTITY CASCADE;\n\n")

        allergen_names = [
            "Glúten", "Laticínios", "Ovos", "Frutos de Casca Rija", "Peixe", 
            "Marisco", "Soja", "Amendoim", "Sésamo", "Mostarda", 
            "Aipo", "Dióxido de Enxofre", "Tremoço", "Moluscos", "Milho"
        ]
        f.write("-- Seed Allergens\n")
        for i, name in enumerate(allergen_names, 1):
            f.write(f"INSERT INTO allergens (id, name) VALUES ({i}, {escape_str(name)});\n")
        f.write("\n")

        f.write("-- Seed Users\n")
        hashed_pw = '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6L6s57OT69.3.8VW'
        goals = ["Perder Peso", "Ganhar Massa", "Manter Peso", "Melhorar Performance"]
        activity_levels = ["Sedentário", "Ligeiro", "Moderado", "Ativo", "Muito Ativo"]
        
        for i in range(1, 11):
            username = f"user{i}"
            full_name = f"Utilizador Teste {i}"
            peso = round(random.uniform(60.0, 95.0), 1)
            altura = round(random.uniform(1.55, 1.95), 2)
            sexo = random.choice(["M", "F"])
            idade = random.randint(18, 60)
            goal = random.choice(goals)
            activity = random.choice(activity_levels)
            target_cal = random.randint(1800, 3000)
            f.write(f"INSERT INTO users (id, username, full_name, hashed_password, peso, altura, sexo, idade, goal, activity_level, target_calories) VALUES ({i}, {escape_str(username)}, {escape_str(full_name)}, {escape_str(hashed_pw)}, {peso}, {altura}, {escape_str(sexo)}, {idade}, {escape_str(goal)}, {escape_str(activity)}, {target_cal});\n")
            num_alg = random.randint(0, 2)
            if num_alg > 0:
                selected_alg_ids = random.sample(range(1, len(allergen_names) + 1), num_alg)
                for alg_id in selected_alg_ids:
                    f.write(f"INSERT INTO user_allergens (user_id, allergen_id) VALUES ({i}, {alg_id});\n")
        f.write("\n")

        f.write("-- Seed Recipes\n")
        recipe_bases = ["Frango", "Salmão", "Atum", "Tofu", "Ovos", "Peru", "Grão", "Feijão", "Massa", "Arroz"]
        recipe_styles = ["Grelhado", "ao Forno", "Salteado", "Cozido", "em Salada", "Estufado"]
        for i in range(1, 51):
            base = random.choice(recipe_bases)
            style = random.choice(recipe_styles)
            name = f"{base} {style} Saudável {i}"
            ing = f"Base de {base}, legumes variados, temperos naturais, azeite."
            inst = f"1. Preparar a base de {base}. 2. {style} os ingredientes. 3. Servir com acompanhamento saudável."
            f.write(f"INSERT INTO recipes (id, name, ingredients, instructions) VALUES ({i}, {escape_str(name)}, {escape_str(ing)}, {escape_str(inst)});\n")
        f.write("\n")

        f.write("-- Seed Restaurants\n")
        restaurant_names = ["Bio Sabor", "Horta no Prato", "Puro Verde", "Saúde na Mesa", "Fit Food", "Natural Gourmet", "The Green Leaf"]
        for i in range(1, 21):
            name = f"{random.choice(restaurant_names)} {i}"
            addr = f"Rua das Flores, {random.randint(1, 200)}, Cidade"
            phone = f"912345{i:03d}"
            f.write(f"INSERT INTO restaurants (id, name, address, phone) VALUES ({i}, {escape_str(name)}, {escape_str(addr)}, {escape_str(phone)});\n")
        f.write("\n")

        f.write("-- Seed Weight Entries\n")
        for u_id in range(1, 11):
            today = datetime.now()
            for i in range(20):
                date_str = (today - timedelta(days=i*7)).strftime("%Y-%m-%d")
                weight = round(75.0 + random.uniform(-2.0, 2.0), 1)
                f.write(f"INSERT INTO weight_entries (user_id, weight, date) VALUES ({u_id}, {weight}, {escape_str(date_str)});\n")
        f.write("\n")

        f.write("-- Seed Diary Days and Meals\n")
        meal_names = {"breakfast": ["Pão Integral", "Iogurte"], "lunch": ["Frango com Arroz"], "snack": ["Fruta"], "dinner": ["Sopa"], "extras": ["Chocolate"]}
        day_id, meal_id = 1, 1
        for u_id in range(1, 11):
            for d in range(15):
                date_key = (datetime.now() - timedelta(days=d)).strftime("%Y-%m-%d")
                f.write(f"INSERT INTO diary_days (id, user_id, date_key, goal, water_liters) VALUES ({day_id}, {u_id}, {escape_str(date_key)}, 2000, 2.0);\n")
                for section in ["breakfast", "lunch", "snack", "dinner"]:
                    name = random.choice(meal_names[section])
                    f.write(f"INSERT INTO diary_meals (id, day_id, section, name, grams, calories, protein, carbs, fat) VALUES ({meal_id}, {day_id}, {escape_str(section)}, {escape_str(name)}, 200, 400, 20, 40, 10);\n")
                    meal_id += 1
                day_id += 1
        f.write("\n")

        f.write("-- Adjust sequences\n")
        for table in ["allergens", "users", "recipes", "restaurants", "diary_days", "diary_meals", "food_history", "weight_entries"]:
            f.write(f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), (SELECT MAX(id) FROM {table}));\n")
        f.write("\nCOMMIT;\n")

    print(f"SUCCESS: {sql_file} generated.")

if __name__ == "__main__":
    generate_sql()
