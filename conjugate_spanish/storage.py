from conjugate_spanish.utils import cs_debug
from string import Template
from conjugate_spanish.verb import Verb
from conjugate_spanish.phrase import Phrase
from conjugate_spanish.nonconjugated_phrase import NonConjugatedPhrase
from aqt import mw
from anki.hooks import addHook, wrap, remHook


class Storage_(object):
    DB_VERSION='0.1.11'
    PHRASE_COLUMNS = ["id", "phrase","definition", "conjugatable", "prefix_words", "prefix", "core_characters", "inf_ending", "inf_ending_index","reflexive", "suffix_words", "conjugation_overrides","applied_overrides","manual_overrides", "base_verb", "root_verb", "generated"]
    
    def __init__(self, mw):
        from anki.hooks import addHook
        self.mw = mw
        self.delete_sql_= self._generate_sql("delete from ${conjugation_overrides_table} where ${phrase_table_name}_id=(select id from ${phrase_table_name} where phrase=?)")   
        # NO     
        self.insert_override_sql_ =self._generate_sql("insert into ${conjugation_overrides_table} (conjugation_overrides_key,${phrase_table_name}_id) select ?, id from ${phrase_table_name} where phrase=?")        
        self.insert_association_sql_ = self._generate_sql("""
            insert into ${associations_table} (${phrase_table_name}_root_phrase,${phrase_table_name}_derived_id, ${phrase_table_name}_root_id) 
                select ?, derived.id, null from ${phrase_table_name} derived where derived.phrase = ?;            
            """)        
        self.select_association_sql_ = self._generate_sql("""select  ${phrase_table_name}_derived_id,
                ${phrase_table_name}_root_id,
                ${phrase_table_name}_root_phrase from ${associations_table} where  ${phrase_table_name}_derived_id in( ?)""")
        # HACK - move the columns to some place
        select_string = "select "+ ", ".join(Storage_.PHRASE_COLUMNS) + " from ${phrase_table_name} "
        self.select_phrase_sql = self._generate_sql(select_string)
        self.insert_phrase_to_note_sql = self._generate_sql("""insert into ${phrase_note_table} (${phrase_table_name}_id,phrase,${note_table_name}_id,model_template_id) 
            values(?,?,?,?)""")
        self._select_phrase_by_note_sql = self._generate_sql("""select ${phrase_columns} from ${phrase_table_name} join ${phrase_note_table} on ${phrase_table_name}.id={phrase_note_table}.${phrase_table_name}_id where ${note_table_name}_id=?""")
        
        self._select_phrase_by_phrase = self._generate_sql("""select ${phrase_columns} from ${phrase_table_name} where phrase = ?""")
        addHook("remNotes", self._remNotes_hook)

    @property
    def db(self):
        return self.mw.col.db
    
    def initialize(self):
        self.addSchema()
        
    @property
    def phrase_table_name(self):
        return 'cs_phrase'
    
    @property
    def associations_table(self):
        return 'cs_associations'
    
    @property
    def conjugation_overrides_table(self):
        return 'cs_conjugation_overrides'
    
    @property
    def phrase_note_table(self):
        return 'cs_phrase_note'
    
    @property
    def note_table_name(self):
        """
        anki notes table
        """
        return 'notes'
    
    @property
    def association_columns(self):
        if not hasattr(self, "_association_columns"):
            self._association_columns = [self._generate_sql(col_name) for col_name in 
                                         ["${phrase_table_name}_derived_id", "${phrase_table_name}_root_id", "${phrase_table_name}_root_phrase"]]
        return self._association_columns
    
    @property
    def sql_substitutions(self):
        return dict(phrase_table_name=self.phrase_table_name, associations_table=self.associations_table, conjugation_overrides_table=self.conjugation_overrides_table,
                  phrase_note_table=self.phrase_note_table,               
                  note_table_name=self.note_table_name,
                  phrase_columns=self.PHRASE_COLUMNS
                  )  
        
    def addSchema(self):        
        # "phrase","definition", "prefix_words", "prefix", "core_characters", "inf_ending", "reflexive", "suffix_words"
        cs_debug(__file__, "addSchema")
        # "phrase","definition","conjugation_overrides","manual_overrides","synonyms","notes"
        dbString = self._generate_sql("""create table if not exists cs_config (
                id                       integer primary key,
                key                text,
                data                text,
                UNIQUE(key) ON CONFLICT REPLACE
                )
            """);
        self.db.executescript(dbString)
        version = self.db.scalar("select data from cs_config where key='version'")
        if version != self.DB_VERSION:
            # HACK future upgrade path needed.
            cs_debug("old version ",version, ": upgrading to version ", self.DB_VERSION)
            self.dropDb()
        
        # TODO : have conjugation_root_phrase_id in ${phrase_table_name} -- the place for the base conjugations *not the base verb*
        # TODO: create root_phrase if does not exist. before inserting  
        # TODO: create the base_verb as a separate from root -- for example "detenerse a [inf]","stop [inf]" -- base verb = detenerse , root -tener
        dbString = self._generate_sql("""
            create table if not exists cs_config (
                id                       integer primary key,
                key                text,
                data                text,
                UNIQUE(key) ON CONFLICT REPLACE
            );
            create table if not exists ${phrase_table_name} (
                id                       integer primary key,
                phrase                   text not null unique,
                definition               text,
                conjugatable             boolean not null default true,
                prefix_words             text,
                prefix                   text,
                core_characters          text,
                inf_ending               text,
                inf_ending_index         integer,
                reflexive                integer,
                suffix_words             text,
                base_verb             text,
                root_verb             text,
                conjugation_root_id      integer,
                parent_phrase_id         integer,
                conjugation_overrides    text,
                applied_overrides        text,
                manual_overrides         text,
                generated                boolean not null default false,
                synonyms                 text,
                notes                    text
            );
            create table if not exists ${phrase_note_table} (
                id                       integer primary key,
                phrase                   text not null,
                ${phrase_table_name}_id     integer,
                ${note_table_name}_id    integer,
                model_template_key       text,
                model_template_id        integer,
                UNIQUE(${phrase_table_name}_id, ${note_table_name}_id, model_template_id) ON CONFLICT REPLACE
            );                    
            create table if not exists ${associations_table} (
                ${phrase_table_name}_derived_id     integer not null,
                ${phrase_table_name}_root_id        integer default null,
                ${phrase_table_name}_root_phrase    text not null,
                UNIQUE (${phrase_table_name}_derived_id, ${phrase_table_name}_root_phrase) ON CONFLICT REPLACE
                FOREIGN KEY(${phrase_table_name}_root_id) REFERENCES ${phrase_table_name}(id),
                FOREIGN KEY(${phrase_table_name}_derived_id) REFERENCES ${phrase_table_name}(id)
            );            
            create table if not exists ${conjugation_overrides_table} (
                id                           integer primary key,
                conjugation_overrides_key text not null,
                ${phrase_table_name}_id                  integer,  
                UNIQUE (${phrase_table_name}_id, conjugation_overrides_key) ON CONFLICT REPLACE
                FOREIGN KEY(${phrase_table_name}_id) REFERENCES ${phrase_table_name}(id)
            );
            insert or replace into cs_config (key, data) values ('version', '"""+self.DB_VERSION+"""'); 
        """)
        cs_debug("Running addSchema script: ", dbString)
        self.db.executescript(dbString)
        self.mw.reset()
        
    def dropDb(self):
        dbString = self._generate_sql("""drop table if exists cs_config;
            drop table if exists $phrase_table_name;
            drop table if exists $associations_table;
            drop table if exists ${conjugation_overrides_table};
            drop table if exists $phrase_note_table""")
        self.db.executescript(dbString)    

    def resetDb(self):
        self.dropDb()
        self.addSchema()
        
    def _generate_sql(self, sql_template_string):
        template = Template(sql_template_string)
        sql_string = template.substitute(**self.sql_substitutions)
        return sql_string
        
    def generate_insert_sql(self, cls):
        table_columns = cls.table_columns()
        table_columns_names = ",".join(table_columns)
        questions = ",".join(["?"] * len(table_columns))
        insert_sql = "insert or replace into "+self.phrase_table_name+"("+table_columns_names+") values ("+questions+")"
        return insert_sql
    
    def batch_insert(self, insert_sql, dbobjects):
        data = map(lambda dbobject: dbobject.sql_insert_values(), dbobjects)
        print(" insert_sql=",insert_sql)
        self.db.executemany(insert_sql, data)
    
    def upsertPhrasesToDb(self, *phrases):
        # delete from the conjugation tables
        delete_data =map(lambda dbobject:[dbobject.full_phrase],phrases)  
        self.db.executemany(self.delete_sql_, delete_data)
        
        # HACK : NOTE: requiring that all phrases be in the same class - not worth fixing at this moment because other things are changing.
        insert_sql = self.generate_insert_sql(phrases[0].__class__)
        self.batch_insert(insert_sql, phrases)
#         for phrase in phrases:
#             if phrase.is_conjugatable:                 
#                 if phrase.is_derived:
#                     parent_verb_str = phrase.root_verb_string
#                     verb_row =self.db.first(self._select_phrase_by_phrase, parent_verb_str)
#                     if verb_row is None: 
#                         Verb(parent_verb_str, conjugation_overrides=phrase.explicit_overrides_string)
#                     base_verb_row =self.db.first(self._select_phrase_by_phrase, phrase.base_verb_string)
#                     if base_verb_row is None: 
#                         pass
        self.create_associations(phrases)
        # HACK : NOTE: requiring that all phrases be in the same class - not worth fixing at this moment because other things are changing.
        if phrases[0].is_conjugatable:
            for verb in phrases:             
                if not verb.is_regular:
                    insert_overrides_data = map(lambda appliedOverride: [appliedOverride, verb.full_phrase], verb.appliedOverrides)
                    self.db.executemany(self.insert_override_sql_, insert_overrides_data)
                        
        # TODO: not completely certain that this is needed but because being called from non ui threads - don't know about transactions
        self.db.commit()
        count = self.db.scalar("select count(*) from "+self.phrase_table_name+ " where "+ (" conjugatable" if phrases[0].is_conjugatable else "not conjugatable"))
        cs_debug("Count = ",count)
        count = self.db.scalar("select count(*) from "+self.conjugation_overrides_table+";")
        cs_debug("overrides Count = ",count)
        
    def create_associations(self, phrases):
        insert_associations_data = []
        for phrase in phrases:
            if phrase.is_derived:
                cs_debug(phrase.full_phrase)
                for derived in phrase.derived_from:
                    insert_associations_data.append([derived, phrase.full_phrase])   
        cs_debug(self.insert_association_sql_)
        self.db.executemany(self.insert_association_sql_, insert_associations_data)
        # connect all roots back to all derived. TODO - limit to 
        self.db.execute(self._generate_sql( "update ${associations_table} set ${phrase_table_name}_root_id=(select id from ${phrase_table_name} where ${associations_table}.${phrase_table_name}_root_phrase=${phrase_table_name}.phrase) where ${phrase_table_name}_root_id is NULL"))
        self.db.commit()
            
    def get_phrases(self, conjugatable=None, phrase=None):
        from .phrase import Phrase
        results = []
        sql_string = self.select_phrase_sql
        where = []
        if conjugatable == True:
            where.append("conjugatable")
        elif conjugatable == False:
            where.append("not conjugatable")
        
        if phrase is not None:
            where.append("phrase LIKE '"+phrase+"'")
        
        if len(where) > 0:
            sql_string = sql_string + " where " + " AND ".join(where)
        
        results_dict = dict()
        for phrase_row in self.db.execute(sql_string):
            phrase =self._load(phrase_row)
            results_dict[phrase.id] = phrase
            results.append(phrase)
        
        return results
    
    def _load(self, phrase_row):
        phrase_dict = dict(zip(Storage_.PHRASE_COLUMNS, phrase_row))
        base_verb_cursor = self.db.execute(self.select_association_sql_, phrase_dict["id"])

        base_verbs = [dict(zip(Storage.association_columns, association))
                                  for association in base_verb_cursor]
        if len(base_verbs) > 0:
            phrase_dict['base_verb'] = base_verbs[0][Storage.association_columns[2]]

        phrase = Phrase.from_dict(phrase_dict)
        return phrase
    
    def get_phrase_from_note(self, note):
        phrase_row = self.db.first(self._select_phrase_by_note_sql, note.id)
        return self._load(phrase_row)
            
    def _create_conjugation_overrides_from_parent(self):
        """
        TODO:
        we have a derived verb
        """
        pass
    
    def _create_placeholder_base_verb(self):
        """
        TODO:
        Handles case where the base verb is not yet in the database.
        we create the base verb as the place to store conjugation overrides.
        this allows other derived verbs to pick up the conjugation overrides.
        """
        pass
        
    def connect_phrase_to_note(self, phrase, note):
        # 2016-09-24: Annoyingly named parameters is not working
        sql_params=[
                    phrase.id,
                    phrase.full_phrase,
                    note.id,
                    note.mid
                    ]
        self.db.execute( self.insert_phrase_to_note_sql, *sql_params)
         
    def _remNotes_hook(self, collection, note_ids):
        """
        Called when notes are removed.
        allow us to clean up if needed
        """
        note_ids_ = [[id] for id in note_ids]
        collection.db.executemany(self._generate_sql("delete from $phrase_note_table where ${note_table_name}_id = ?"), note_ids_)
            
Storage = Storage_(mw)
addHook('profileLoaded', Storage.initialize)