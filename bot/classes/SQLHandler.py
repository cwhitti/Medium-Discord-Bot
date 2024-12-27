from sqlmodel import SQLModel, Field, create_engine, Session, Relationship, select

# Custom handler
class SQLHandler:
    def __init__(self, db_path, dbg=False) -> None:
        self.engine = create_engine( f"sqlite:///{db_path}" )  
        self.dbg = dbg

        if self.dbg:
            SQLModel.metadata.drop_all(self.engine)
            SQLModel.metadata.create_all(self.engine)

    def check_exists(self, model: SQLModel, filters: dict) -> bool:
        """
        Check if a record exists in the database based on filters.

        Args:
            model (SQLModel): The model class to query.
            filters (dict): A dictionary of field names and values to filter by.

        Returns:
            bool: True if a record exists, False otherwise.

        Example Usage:
            exists = self.check_exists(Student, {"id": "S001"})
        """
        with Session(self.engine) as session:
            query = select(model)
            for key, value in filters.items():
                query = query.where(getattr(model, key) == value)
            result = session.exec(query).first()
            return result is not None
        
    def insert(self, model_instance: SQLModel) -> bool:
        """
        Insert a new record into the database, if it doesn't already exist.
        
        Example Usage: 
            handler.insert(Course(id=1, name="CS126"))
            handler.insert(Student(id="S001", name="John Doe", main_class=1, lab_class=1))

        """
        model = type(model_instance)
        filters = {"id": model_instance.id}  # Assuming 'id' is the unique field
        if self.check_exists(model, filters):
            return False
        else:
            with Session(self.engine) as session:
                session.add(model_instance)
                session.commit()
                return True
            
    def needs_update(self, model: SQLModel, record_id: int, updates: dict) -> bool:
        """
        Check if a record in the database needs to be updated based on the provided information.

        Args:
            model (SQLModel): The model class to query.
            record_id (int): The ID of the record to check.
            updates (dict): A dictionary of field names and their desired values.

        Returns:
            bool: True if the record needs to be updated, False otherwise.

        Example Usage:
            updates = {"name": "CS126L", "section": "002"}
            needs_update = handler.needs_update(Course, record_id=1, updates=updates)
        """
        with Session(self.engine) as session:
            # Retrieve the existing record
            statement = select(model).where(model.id == record_id)
            record = session.exec(statement).first()

            # If the record does not exist, no update is needed
            if not record:
                return False

            # Compare existing values with the updates
            for key, value in updates.items():
                if getattr(record, key) != value:
                    return True  # An update is needed if any value differs

        return False  # No updates needed
    def remove(self, model: SQLModel, record_id: int) -> bool:
        """Remove a record from the database by ID."""
        with Session(self.engine) as session:
            statement = select(model).where(model.id == record_id)
            result = session.exec(statement).first()
            if result:
                session.delete(result)
                session.commit()
                return True
        return False

    def summary(self) -> dict:
        """
        Retrieve a summary of the database, including the number of courses and students.
        
        Returns:
            dict: A dictionary with counts of courses and students.
        """
        with Session(self.engine) as session:
            course_count = session.exec(select(Course)).all()
            return {
                "course_count": len(course_count),
                }
        
    def update(self, model: SQLModel, record_id: int, updates: dict) -> bool:
        """Update a record in the database."""
        with Session(self.engine) as session:
            # Retrieve the record by ID
            statement = select(model).where(model.id == record_id)
            record = session.exec(statement).first()

            if record:
                # Apply updates
                for key, value in updates.items():
                    setattr(record, key, value)
                session.add(record)
                session.commit()
                return True
            
        return False


    def retrieve(self, model: SQLModel, filters: dict = None) -> list[SQLModel]:
        """
        Retrieve records from the database based on optional filters.
        
        Args:
            model (SQLModel): The SQLModel class to query.
            filters (dict, optional): A dictionary of column-value pairs for filtering.
        
        Returns:
            list[SQLModel]: A list of records that match the filters.
        """
        with Session(self.engine) as session:
            # Start with a base query
            query = select(model)

            # Apply filters if provided
            if filters:
                for key, value in filters.items():
                    # Use getattr to dynamically access model fields
                    query = query.where(getattr(model, key) == value)

            # Execute the query and return results as a list
            results = session.exec(query).all()
            return results

# Course Table
class Course(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, default=None )
    section: str = Field(max_length=3, default=None, nullable=True)

def _main():

    # Initialize handler
    handler = SQLHandler()

    # Insert a course and a student
    handler.insert( Course(id=1001, name="CS126") )
    handler.insert( Course(id=1002, name="CS126L", section="001") )
    handler.insert( Course(id=1003, name="CS126L", section="002") )
    handler.insert( Course(id=1004, name="CS126L", section="003") )
    handler.insert( Course(id=5005, name="CS249", section="001") )
    handler.insert( Course(id=5006, name="CS249", section="002") )

    # We wanna make some updates!
    updates={"name": "CS126 - Combo Class"}
    # Update a course's name
    if handler.needs_update(Course, record_id=1001, updates=updates):
        handler.update(Course, record_id=1001, updates=updates)

    # Retrieve all courses
    courses = handler.retrieve( Course )
    print(courses)

#_main()