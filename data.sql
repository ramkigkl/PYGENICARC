/**This is necessary to display the list of courses on your website. You can insert the following initial data into the courses collection. Run this in the Mongo shell or use a tool like MongoDB Compass.

bash
Copy code**/
use pygenicarc
db.courses.insertMany([
    {
        title: "DevOps",
        description: "Learn DevOps tools and practices.",
        category: "Development"
    },
    {
        title: "Web Development",
        description: "Become a web developer using HTML, CSS, and JavaScript.",
        category: "Development"
    },
    {
        title: "Full Stack Development",
        description: "Master both frontend and backend development.",
        category: "Development"
    },
    {
        title: "Data Analytics",
        description: "Analyze and visualize data effectively.",
        category: "Data Science"
    }
])