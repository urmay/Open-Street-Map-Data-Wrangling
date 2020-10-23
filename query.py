"""
Queries
"""

import csv, sqlite3

def number_of_nodes():
	result = cur.execute('SELECT COUNT(*) FROM nodes')
	return result.fetchone()[0]

def number_of_ways():
	result = cur.execute('SELECT COUNT(*) FROM ways')
	return result.fetchone()[0]

def number_of_unique_users():
	result = cur.execute('SELECT COUNT(DISTINCT(e.uid)) \
            FROM (SELECT uid FROM nodes UNION ALL SELECT uid FROM ways) e')
	return result.fetchone()[0]
    
def top_contributing_users():
	users = []
	for row in cur.execute('SELECT e.user, COUNT(*) as num \
            FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) e \
            GROUP BY e.user \
            ORDER BY num DESC \
            LIMIT 10'):
		users.append(row)
	return users

def number_of_users_contributing_once():
	result = cur.execute('SELECT COUNT(*) \
            FROM \
                (SELECT e.user, COUNT(*) as num \
                 FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) e \
                 GROUP BY e.user \
                 HAVING num=1) u')
	return result.fetchone()[0]

def common_ammenities():
    amenities=[]
    
    for row in cur.execute('SELECT value, COUNT(*) as num \
            FROM nodes_tags \
            WHERE key="amenity" \
            GROUP BY value \
            ORDER BY num DESC \
            LIMIT 10'):
        amenities.append(row)
    return amenities
       
def top_religion():
    religion_list =[]
    
    for row in cur.execute('SELECT value, COUNT(*) as num \
            FROM nodes_tags \
                JOIN (SELECT DISTINCT(id) FROM nodes_tags WHERE value="place_of_worship") i \
                ON nodes_tags.id=i.id \
            WHERE nodes_tags.key="religion" \
            GROUP BY nodes_tags.value \
            ORDER BY num DESC \
            LIMIT 5'):
        religion_list.append(row)
	
    return religion_list

def popular_cuisines():
    cuisines_list =[]
    
    for row in cur.execute('SELECT value, COUNT(*) as count \
            FROM nodes_tags \
            JOIN (SELECT DISTINCT(id) FROM nodes_tags WHERE value="restaurant") i \
            ON nodes_tags.id=i.id \
            WHERE nodes_tags.key="cuisine" \
            GROUP BY nodes_tags.value \
            ORDER BY count DESC\
            LIMIT 10'):
        cuisines_list.append(row)
        
    return cuisines_list

def top_postcodes():
    top_postcode_list=[]
    
    
    for row in cur.execute('SELECT value, COUNT(*) as count\
                           FROM nodes_tags \
                           WHERE key = "postcode"\
                           GROUP BY nodes_tags.value \
                           ORDER BY count DESC\
                           LIMIT 10'):
        top_postcode_list.append(row)
    return top_postcode_list


def top_type_of_buildings():
    building_list=[]
    
    
    for row in cur.execute('SELECT value, COUNT(*) as count\
                           FROM ways_tags \
                           WHERE key = "building"\
                           GROUP BY ways_tags.value \
                           ORDER BY count DESC\
                           LIMIT 10'):
        building_list.append(row)
    return building_list


if __name__ == '__main__':
	
	con = sqlite3.connect("/H:/udacity_course_file/DW_Project/my_dw_project/ahmedabad_1.db")
	cur = con.cursor()

print "Number of nodes: " , number_of_nodes()
print "Number of ways: " , number_of_ways()
print "Number of unique users: " , number_of_unique_users()
print "Top contributing users: " , top_contributing_users()
print "Number of users contributing once: " , number_of_users_contributing_once()
# Exploring further data
print "Common ammenities: " , common_ammenities()
print "Top Religion: " , top_religion()
print "Popular Cuisines: " , popular_cuisines()
print "Top postcodes:",top_postcodes()	
print "Top Types of Buildings:",top_type_of_buildings()  