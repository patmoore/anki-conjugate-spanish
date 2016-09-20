from conjugate_spanish.utils import cs_debug
from string import Template
from aqt import mw
import conjugate_spanish
from conjugate_spanish.verb import Verb
from conjugate_spanish.nonconjugated_phrase import NonConjugatedPhrase

class Storage_(object):
    DB_VERSION='0.1.1'
    PHRASE_COLUMNS = ["id", "phrase","definition", "conjugatable", "prefix_words", "prefix", "core_characters", "inf_ending", "inf_ending_index","reflexive", "suffix_words", "explicit_overrides", "overrides","applied_overrides","manual_overrides"]
    def __init__(self, mw):
        self.mw = mw
        self.delete_sql_= self.generate_sql_("delete from ${conjugation_overrides_table} where ${phrase_table_name}_id=(select id from ${phrase_table_name} where phrase=?)")   
        # NO     
        self.insert_override_sql_ =self.generate_sql_("insert into ${conjugation_overrides_table} (conjugation_overrides_key,${phrase_table_name}_id) select ?, id from ${phrase_table_name} where phrase=?")        
        self.insert_association_sql_ = self.generate_sql_("""insert into ${associations_table} (${phrase_table_name}_root_phrase,${phrase_table_name}_derived_id, ${phrase_table_name}_root_id) 
            select ?, derived.id, null
               from ${phrase_table_name} derived where derived.phrase = ?""")
        self.insert_association_sql_ = self.generate_sql_("""insert into ${associations_table} (${phrase_table_name}_root_phrase,${phrase_table_name}_derived_id, ${phrase_table_name}_root_id) 
            select ?, derived.id, null
               from ${phrase_table_name} derived where derived.phrase = ?""")
        # HACK - move the columns to some place
        select_string = "select "+ ", ".join(Storage_.PHRASE_COLUMNS) + " from ${phrase_table_name} "
        self.select_phrase_sql = self.generate_sql_(select_string)

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
    def sql_substitutions(self):
        return dict(phrase_table_name=self.phrase_table_name, associations_table=self.associations_table, conjugation_overrides_table=self.conjugation_overrides_table,
                  phrase_note_table=self.phrase_note_table,
                  # anki notes table
                  note_table_name='notes')  
        
    def addSchema(self):        
        # "phrase","definition", "prefix_words", "prefix", "core_characters", "inf_ending", "reflexive", "suffix_words"
        cs_debug(__file__, "addSchema")
        # "phrase","definition","conjugation_overrides","manual_overrides","synonyms","notes"
        dbString = self.generate_sql_("""create table if not exists cs_config (
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
        
        dbString = self.generate_sql_("""
            create table if not exists cs_config (
                id                       integer primary key,
                key                text,
                data                text,
                UNIQUE(key) ON CONFLICT REPLACE
                );
            create table if not exists $phrase_table_name (
                id                       integer primary key,
                phrase                   text not null unique,
                definition               text,
                conjugatable             boolean not null default true,
                prefix_words             text,
                prefix                   text,
                core_characters          text,
                inf_ending               text,
                inf_ending_index         integer,
                reflexive                boolean,
                suffix_words             text,
                explicit_overrides       text,
                overrides                text,
                applied_overrides        text,
                manual_overrides         text,
                synonyms                 text,
                notes                    text
            );
            create table if not exists $phrase_note_table (
                id                       integer primary key,
                phrase                   text not null unique,
                ${phrase_table_name}_id     integer,
                ${note_table_name}_id    integer,
                model_template_id        integer
            );                    
            create table if not exists $associations_table (
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
            
        cs_debug("dbString=",dbString)
        self.db.executescript(dbString)
        mw.reset()
        
    def dropDb(self):
        dbString = self.generate_sql_("""drop table if exists cs_config;
            drop table if exists $phrase_table_name;
            drop table if exists $associations_table;
            drop table if exists ${conjugation_overrides_table};
            drop table if exists $phrase_note_table""")
        self.db.executescript(dbString)

    def resetDb(self):
        self.dropDb()
        self.addSchema()
        
    def generate_sql_(self, sql_template_string):
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
    
    def upsertPhrasesToDb(self, phrases):
        insert_sql = self.generate_insert_sql(NonConjugatedPhrase)
        self.batch_insert(insert_sql, phrases)
        self.create_associations(phrases)

        count = self.db.scalar("select count(*) from "+self.phrase_table_name+" where not conjugatable")
        cs_debug("Count = ",count)
 
    def upsertVerbsToDb(self, verbs):
        # delete from the conjugation tables
        delete_data =map(lambda dbobject:[dbobject.full_phrase],verbs)  
        self.db.echo = True      
        self.db.executemany(self.delete_sql_, delete_data)
        
        insert_sql = self.generate_insert_sql(Verb)
        self.batch_insert(insert_sql, verbs)
        self.create_associations(verbs)
        for verb in verbs:             
            if not verb.is_regular:
                insert_overrides_data = map(lambda appliedOverride: [appliedOverride, verb.full_phrase], verb.appliedOverrides)
                cs_debug("associations",insert_overrides_data)
                self.db.executemany(self.insert_override_sql_, insert_overrides_data)
                        
        count = self.db.scalar("select count(*) from "+self.phrase_table_name+ " where conjugatable")
        cs_debug("Count = ",count)
        count = self.db.scalar("select count(*) from "+self.conjugation_overrides_table+";")
        cs_debug("Count = ",count)
        
    def create_associations(self, phrases):
        insert_associations_data = []
        for phrase in phrases:
            if phrase.is_derived:
                cs_debug(phrase.full_phrase)
                for derived in phrase.derived_from:
                    insert_associations_data.append([derived, phrase.full_phrase])   
        cs_debug(self.insert_association_sql_)
        self.db.executemany(self.insert_association_sql_, insert_associations_data)
            
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
        for phrase_row in self.db.execute(sql_string):
            phrase_dict = dict(zip(Storage_.PHRASE_COLUMNS, phrase_row))
            results.append(Phrase.from_dict(phrase_dict))

        return results
            
Storage = Storage_(mw)