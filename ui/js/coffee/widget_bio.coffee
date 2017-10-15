bio = (json, state) ->
        obj = document.createElement('div')
        if json.found
            # First commit
            firstcommit = "Never"
            if json.bio.firstCommit
                firstcommit = new Date(json.bio.firstCommit*1000).toDateString()
            # First authorship
            firstauthor = "Never"
            if json.bio.firstAuthor
                firstauthor = new Date(json.bio.firstAuthor*1000).toDateString()
            # First email
            firstemail = "Never"
            if json.bio.firstEmail
                firstemail = new Date(json.bio.firstEmail*1000).toDateString()
            obj.innerHTML += '
                <div class="media event">
                    <a class="pull-left">
                        <img style="width: 128px; height: 128px;" src="https://secure.gravatar.com/avatar/' + json.bio.gravatar + '.png?d=identicon&size=128"/>
                    </a>
                    <div class="media-body">
                        <h1>'+json.bio.name+'</h1>
                        <h2>' + json.bio.email + '</h2><br/>
                        <h3>First code commit: ' + firstcommit + '</h3>
                        <h3>First code authorship: ' + firstauthor + '</h3>
                        <h3>First email sent: ' + firstemail + '</h3>                        
                    </div>
                </div>
                '
            namecard = mk('h2')
            groups = []
            if json.bio.tags
                for tag in json.bio.tags
                    if tag != '_untagged'
                        groups.push(tag)
            if groups.length > 0
                namecard.appendChild(mk('br'))
                namecard.appendChild(txt("Part of: " + groups.join(", ")))
            a = mk('a')
            set(a, 'href', 'javascript:void(affiliate("' + json.bio.id + '"));')
            app(a, txt("Set a tag"))
            
            egroups = []
            if json.bio.alts and json.bio.alts.length
                for tag in json.bio.alts
                    egroups.push(tag)
            if egroups.length > 0
                namecard.appendChild(mk('br'))
                namecard.appendChild(txt("Also known as: " + egroups.join(", ")))
            a2 = mk('a')
            a2.style.marginLeft = "8px"
            set(a2, 'href', 'javascript:void(altemail("' + json.bio.id + '"));')
            app(a2, txt("Add alt email"))
            
            sp = mk('span')
            set(sp, 'id', 'tags_' + json.bio.id)
            app(obj, namecard)
            app(obj, a)
            app(obj, a2)
            app(obj, sp)
            
        else
            obj.innerHTML = "Person not found :/"
        state.widget.inject(obj, true)
