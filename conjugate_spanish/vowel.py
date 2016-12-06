class Vowels_():
    """
    Long form creation allows developers to easily see if all needed vowel combinations are handled.
    Fancy programatic creation could result in a bug of missing some vowel combination.
    """
     
    
    """
    Long form creation allows developers to easily see if all needed vowel combinations are handled.
    Fancy programatic creation could result in a bug of missing some vowel combination.
    """
    
    # TODO - need to verify accent rules!
    
    # used to preserve order.
    # non-accented because we check first for accented
    
    def __init__(self):        
        a = 'a'
        e = 'e'
        i = 'i'
        o = 'o'
        u = 'u'
        a_a = 'á'
        e_a = 'é'
        i_a = 'í'
        o_a = 'ó'
        u_a = 'ú'
        u_u = 'ü'
        a_any = [a, a_a]
        e_any = [e, e_a]
        i_any = [i, i_a]
        o_any = [o, o_a]
        u_any = [u, u_a, u_u]
        y = 'y'
        i_eq = [ i, y ]
        i_eq_group = re_group(i_eq)
        qu_gu = "(?:[gq]["+u+u_u+"])"
        h = 'h'
        self.unaccented = unaccented = [a,e,i,o,u]
        self.accented = accented = [a_a, e_a, i_a, o_a, u_a]
        self.accented_vowel_check = re_compile(re_group(accented))
        self._replace_accents = [ [re_compile(accented[i]), unaccented[i] ] for i in range(len(accented))]
        self._all = self.all = [ *a_any, *e_any, *i_any, *o_any, *u_any, y ]
        self._any =  [ "".join(a_any), "".join(e_any), "".join(i_any), "".join(o_any), "".join(u_any) ]
        self.all_group = all_group = re_group(self._all)
        self.consonants = consonants = re_group(self._all, True)
        
        strong = [ a, a_a, e, e_a, o, o_a ]
        weak_unaccented = [ i, u, y ]
        self.to_accent_mapping = { a: a_a,
                              e: e_a,
                              i: i_a,
                              o: o_a,
                              u: u_a }
        # combinations with 'h' in the middle - his silent does not break up dipthongs
        # # http://www.123teachme.com/learn_spanish/diphthongs_and_triphthongs
        # note: ou is not a valid dipthong
        for strong_vowel in [ a, e, o ]:
            strong_accent = self.to_accent_mapping[strong_vowel]
            for weak_vowel in weak_unaccented:
                # y does not have the h??
                # ay, ey, oy
                # yo, ya ( i don't know about ye ) but just in case... ) 
                for h_ in [h,'']:
                    self.to_accent_mapping[weak_vowel+h_+strong_vowel] = weak_vowel+h_+strong_accent
                    if not(strong_vowel == o and weak_vowel == u):
                        # note: ou is not a valid dipthong (not certain) but uho /uo is...
                        self.to_accent_mapping[strong_vowel+h_+weak_vowel] = strong_accent+h_+weak_vowel
            
        # >>>>> Note: qu and gu are treated special!
        self.to_accent_mapping[u+i] = u+i_a
        self.to_accent_mapping[u+y] = u+i_a
        self.from_accent_mapping = { value: key for key, value in self.to_accent_mapping.items()}
        
        strong_group=re_group(strong)
        weak_group = re_group(weak_unaccented)    #  a trip-/dip- thong is accented only on the strong vowels 
        three_letter_combinations = []
        two_letter_combinations = []
        # is there a "ahy" combination?  
        three_letter_combinations.append(re_group([*a_any,*e_any])+h+weak_group)
        # o does not go with u ..?
        three_letter_combinations.append(re_group(o_any)+h+i_eq_group)
        two_letter_combinations.append(re_group([*a_any,*e_any])+weak_group)
        # o does not go with u ..?
        two_letter_combinations.append(re_group(o_any)+i_eq_group)
        
        three_letter_combinations.append(weak_group+h+strong_group)
        two_letter_combinations.append(weak_group+strong_group)
        
        for unaccented_, accented_ in [[u+a+y, u+a_a+y],
                                     [u+e+y, u+e_a+y],
                                     [u+a+u, u+a_a+u],
                                     [u+a+i, u+a_a+i],
                                     [i+a+i, i+a_a+i],
                                     [i+e+i, i+e_a+i]]:
            self.to_accent_mapping[unaccented_] = accented_
    
        
        three_letter_combinations.extend([u+re_group([*a_any,*e_any])+y,
                                          # situáis 
                                          u+re_group(a_any)+re_group([u,i]),
                                          # guiáis, estudiéis
                                          i+re_group([*a_any,*e_any])+i])
        
        two_letter_combinations.extend([
                                        # ui, uy
                                        u+re_group([*i_any,y])])
                                        

        # possible combinations are broken up to avoid having to be super exact on the regex rules ( also makes much more readable)
        # in onle case we want to match on the dipthongs / triphongs first before single vowels.
        """
        Accent a vowel explicitly UNLESS there is an accent already
        The rules on accenting in spanish is the last vowel if the word ends in a consonent other than n or s
        Otherwise the second to last vowel.
        If the vowel to be accented is a strong-weak (au,ai,ei,... ) or a weak-strong pair (ua,ia, ... ) the strong vowel of the pair gets the accent
        TODO: NOTE: an h between 2 vowels does not break the diphthong
        https://en.wikipedia.org/wiki/Spanish_irregular_verbs
        Remember that the presence of a silent h does not break a diphthong, so a written accent is needed anyway in rehúso.
        http://www.123teachme.com/learn_spanish/diphthongs_and_triphthongs
        I don't feel i understand the rules correctly.
        """
        # looking for the biggest valid combination of vowels - remember:
        #    1. 2 strong vowels cannot be together
        #    2. special h usecase
        #    3. special handling of y
        #    4. special handling of qu, gu
        # note: order is important here
        # first rule is to look for accent already present. - if present then immediately done.
        self.accent_rules = [re_compile('^(.*?)'+"("+re_group(accented)+")(.*)()$")]
        three_letter_groups = "(?:"+"|".join(three_letter_combinations)+")"
        two_letter_groups = "(?:"+"|".join(two_letter_combinations)+")"
        combinations = [ three_letter_groups, two_letter_groups, all_group]
        for vowels_to_accent in combinations:
            for weak_beginning in ['^(.*?'+qu_gu+')','^(.*?)']:
                for last in combinations:
                    self.accent_rules.extend([
                                              # could have double vowel ending. 
                                              re_compile(weak_beginning+"("+vowels_to_accent+")("+consonants+"*)("+qu_gu+last+'[ns]{0,2})$'),
                                              re_compile(weak_beginning+"("+vowels_to_accent+")("+consonants+"*)("+last+'[ns]{0,2})$')
                                              ])
                self.accent_rules.extend([
                                              # ends in required consonants 
                                              re_compile(weak_beginning+"("+vowels_to_accent+")("+consonants+'+)()$'),
                                              re_compile("^("+consonants+"*)("+vowels_to_accent+')()()$')
                                              ])
        print(self.accent_rules)
        # used to find the vowel groups for displaying vowels in words.
#         self.vowel_groups = re_compile("("+"|".join([*three_letter_combinations, *two_letter_groups, *all]) +")")

    def any(self, vowel):
        for an_any in self._any:
            if an_any.find(vowel) >= 0:
                return an_any
        return vowel
    
    def re_any_string(self, string_):
        regex_str = ''
        for char in string_:
            reg_chars = self.any(char)
            if len(reg_chars) == 1:
                regex_str += reg_chars
            else:
                regex_str += '['+reg_chars+']'
        return regex_str    
    #TODO needs more work
    # need to pick out the exact vowel to accent.
    def find_accented(self, word):
        for accent_rule in self.accent_rules:
            match = accent_rule.match(word)
            if match is not None:
                break
        return match
        
    def accent(self, word):
        match = self.find_accented(word)
        if match:
            accented = match.group(2) if match.group(2) in self.from_accent_mapping else self.to_accent_mapping[match.group(2)]
            
            result = match.group(1)+accented+match.group(3)+match.group(4)
            print(match.groups())
            print("word="+word+";accent-->"+result)
            return result
        else:
            cs_debug("no vowels in "+word)
            return word
    def accent_at(self, string_, index_=None):
        """
        allow the vowel to already be accented
        """
        if index_ is None:
            index_ = len(string_)-1
        
        vowel = string_[index_]
        if vowel in self.from_accent_mapping:
            # already accented
            return string_
        elif vowel in self.to_accent_mapping:
            result = string_[:index_] + self.to_accent_mapping[vowel] + string_[index_+1:]
            return result
        else:
            raise Exception(string_+" at index="+index_+" there is no vowel.")
            
    def remove_accent(self, string_):
        """
        intentionally removes all accents
        """       
        result = string_ 
        for regex, replace in self._replace_accents:
            result = regex.sub(replace, result)
        return result
    
Vowels = Vowels_()
if True:
    for word in ['irgue', 'repite', 'se', 'cambia']:
        answer = Vowels.find_accented(word)