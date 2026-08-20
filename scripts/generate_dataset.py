import pandas as pd
import random

vehicles = [
    ("Swift","Maruti","Car",1197,5,89,"Hatchback"),
    ("Baleno","Maruti","Car",1197,5,89,"Hatchback"),
    ("Dzire","Maruti","Car",1197,5,89,"Sedan"),
    ("Brezza","Maruti","Car",1462,5,103,"SUV"),
    ("Fronx","Maruti","Car",1197,5,99,"SUV"),
    ("Grand Vitara","Maruti","Car",1490,5,114,"SUV"),
    ("Nexon","Tata","Car",1497,5,113,"SUV"),
    ("Punch","Tata","Car",1199,5,86,"SUV"),
    ("Harrier","Tata","Car",1956,5,168,"SUV"),
    ("Safari","Tata","Car",1956,7,168,"SUV"),
    ("Altroz","Tata","Car",1199,5,88,"Hatchback"),
    ("Tiago","Tata","Car",1199,5,86,"Hatchback"),
    ("Creta","Hyundai","Car",1497,5,115,"SUV"),
    ("Venue","Hyundai","Car",1493,5,113,"SUV"),
    ("Verna","Hyundai","Car",1482,5,158,"Sedan"),
    ("i20","Hyundai","Car",1197,5,82,"Hatchback"),
    ("Sonet","Kia","Car",1493,5,115,"SUV"),
    ("Seltos","Kia","Car",1497,5,115,"SUV"),
    ("Carens","Kia","Car",1493,7,115,"MPV"),
    ("XUV700","Mahindra","Car",2198,7,182,"SUV"),
    ("Scorpio N","Mahindra","Car",2198,7,172,"SUV"),
    ("Thar","Mahindra","Car",2184,4,130,"SUV"),
    ("City","Honda","Car",1498,5,121,"Sedan"),
    ("Elevate","Honda","Car",1498,5,121,"SUV"),
    ("Virtus","Volkswagen","Car",1498,5,148,"Sedan"),
    ("Taigun","Volkswagen","Car",1498,5,148,"SUV"),
    ("Kushaq","Skoda","Car",1498,5,148,"SUV"),
    ("Slavia","Skoda","Car",1498,5,148,"Sedan"),
    ("Apache RTR 160","TVS","Bike",160,2,16,"Bike"),
    ("Apache RTR 200","TVS","Bike",198,2,20,"Bike"),
    ("Ronin","TVS","Bike",225,2,20,"Bike"),
    ("Raider 125","TVS","Bike",124,2,11,"Bike"),
    ("Pulsar N160","Bajaj","Bike",164,2,16,"Bike"),
    ("Pulsar NS200","Bajaj","Bike",199,2,24,"Bike"),
    ("Dominar 400","Bajaj","Bike",373,2,40,"Bike"),
    ("Splendor Plus","Hero","Bike",97,2,8,"Bike"),
    ("Xpulse 200","Hero","Bike",200,2,18,"Bike"),
    ("Xtreme 160R","Hero","Bike",163,2,15,"Bike"),
    ("Shine","Honda","Bike",125,2,10,"Bike"),
    ("SP125","Honda","Bike",125,2,10,"Bike"),
    ("Hornet 2.0","Honda","Bike",184,2,17,"Bike"),
    ("CB350","Honda","Bike",348,2,21,"Bike"),
    ("Classic 350","Royal Enfield","Bike",349,2,20,"Bike"),
    ("Hunter 350","Royal Enfield","Bike",349,2,20,"Bike"),
    ("Meteor 350","Royal Enfield","Bike",349,2,20,"Bike"),
    ("Himalayan 450","Royal Enfield","Bike",452,2,40,"Bike"),
    ("R15 V4","Yamaha","Bike",155,2,18,"Bike"),
    ("MT15","Yamaha","Bike",155,2,18,"Bike"),
    ("FZ-S","Yamaha","Bike",149,2,12,"Bike"),
    ("Duke 200","KTM","Bike",199,2,25,"Bike"),
    ("Duke 390","KTM","Bike",399,2,46,"Bike"),
    ("RC 390","KTM","Bike",399,2,46,"Bike")
]

records = []

for year in [2025]:
    for vehicle in vehicles:
        name, brand, vtype, engine, seats, power, body = vehicle

        for variant in range(1, 2):

            if vtype == "Car":
                price = random.randint(600000, 4500000)
                mileage = random.randint(14, 28)
            else:
                price = random.randint(80000, 400000)
                mileage = random.randint(28, 75)

            fuel = random.choice(
                ["Petrol", "Diesel", "Hybrid", "Electric"]
            )

            transmission = random.choice(
                ["Manual", "Automatic"]
            )

            records.append([
                name,
                brand,
                vtype,
                year,
                price,
                mileage,
                fuel,
                transmission,
                random.randint(3, 5),
                engine,
                seats,
                power,
                random.randint(90, 400),
                body,
                random.randint(1, 8),
                random.choice(["Yes", "No"]),
                random.randint(150, 250),
                random.randint(200, 700),
                random.randint(3000, 15000),
                random.randint(10000, 60000)
            ])

columns = [
    "name",
    "brand",
    "type",
    "model_year",
    "price",
    "mileage",
    "fuel_type",
    "transmission",
    "safety_rating",
    "engine_cc",
    "seating_capacity",
    "power_bhp",
    "torque_nm",
    "body_type",
    "airbags",
    "abs",
    "ground_clearance",
    "boot_space",
    "service_cost",
    "insurance_cost"
]

df = pd.DataFrame(records, columns=columns)

df.to_csv(
    "datasets/vehicles.csv",
    index=False
)

print("Dataset Created Successfully")
print("Total Records:", len(df))
