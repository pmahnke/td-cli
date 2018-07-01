from todo.services.base import BaseService


GLOBAL = 'global'


class GroupService(BaseService):
    def _translate_name(self, name):
        if name is None:
            return None
        return name.strip().lower()

    def _is_global(self, name):
        return name is None or self._translate_name(name) == GLOBAL

    def initialise_table(self):
        self.cursor.execute(
            """
            CREATE TABLE "group"(
                name TEXT PRIMARY KEY NOT NULL,
                in_use BOOLEAN NOT NULL DEFAULT 0
            );
            """
        )

    # POST
    def add(self, name):
        if self._is_global(name):
            raise Exception('"global" is a reserved group name. You can`t create that group')

        self.cursor.execute(
            """
            INSERT INTO "group" (name)
            VALUES (?);
            """,
            (self._translate_name(name), )
        )
        self.connection.commit()
        return name

    # DELETE
    def delete(self, name):
        if self._is_global(name):
            raise Exception('"global" is a reserved group name. You can`t delete that group')
        self.cursor.execute(
            """
            DELETE FROM "group"
            WHERE name = ?;
            """,
            (name, )
        )
        self.connection.commit()

    # PUT
    def edit_name(self, new_name, old_name):
        self.cursor.execute(
            """
            UPDATE "group"
            SET name = ?
            WHERE name = ?;
            """,
            (self._translate_name(new_name), self._translate_name(old_name))
        )
        self.connection.commit()

    def use(self, name):
        group_exists = self.get(name) or self._is_global(name)

        if not group_exists:
            raise Exception('Group "{}" not found'.format(name))

        self.cursor.execute(
            """
            UPDATE "group"
            SET in_use = 0
            """
        )

        self.cursor.execute(
            """
            UPDATE "group"
            SET in_use = 1
            WHERE name = ?;
            """,
            (self._translate_name(name), )
        )
        self.connection.commit()

    # GET
    def get(self, name):
        if self._is_global(name):
            return (None, )

        self.cursor.execute(
            """
            SELECT name
            FROM "group"
            WHERE name = ?;
            """,
            (self._translate_name(name), )
        )
        return self.cursor.fetchone()

    def get_active_group(self):
        self.cursor.execute(
            """
            SELECT name
            FROM "group"
            WHERE in_use = 1;
            """
        )
        return self.cursor.fetchone() or (None, )

    def get_all(self):
        self.cursor.execute(
            """
            SELECT IFNULL(name, ?), todos.items, todos.uncompleted, todos.completed
            FROM (
                SELECT group_name,
                   COUNT(*) as items,
                   SUM(completed = 0) as uncompleted,
                   SUM(completed = 1) as completed
                FROM todo
                GROUP BY group_name
            ) todos
            LEFT OUTER JOIN "group" ON todos.group_name = name
            UNION ALL
            SELECT name, 0, 0, 0
            FROM "group"
            LEFT OUTER JOIN todo ON todo.group_name = name
            WHERE todo.group_name IS NULL;
            """,
            (GLOBAL, )
        )
        return self.cursor.fetchall()