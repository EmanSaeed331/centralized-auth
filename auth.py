import os
from typing import Optional, Tuple
from ldap3 import Server, Connection, ALL, SUBTREE
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()

# LDAP Configuration with defaults matching our Docker setup
LDAP_SERVER = os.getenv("LDAP_SERVER", "openldap")
LDAP_PORT = int(os.getenv("LDAP_PORT", "389"))
LDAP_BASE_DN = os.getenv("LDAP_BASE_DN", "dc=example,dc=org")
LDAP_ADMIN_DN = f"cn=admin,{LDAP_BASE_DN}"
LDAP_ADMIN_PASSWORD = "admin"

class LDAPAuth:
    @staticmethod
    def find_user_dn(username: str) -> Optional[str]:
        """Find the correct DN for a user, handling case variations."""
        server = Server(LDAP_SERVER, port=LDAP_PORT, get_info=ALL)
        
        try:
            # Use admin credentials to search for the user
            admin_conn = Connection(
                server,
                user=LDAP_ADMIN_DN,
                password=LDAP_ADMIN_PASSWORD,
                auto_bind=True
            )
            
            # Search for the user by uid (case-insensitive) or cn
            search_filter = f"(|(uid={username.lower()})(cn={username})(cn={username.capitalize()}))"
            
            admin_conn.search(
                search_base=f"ou=users,{LDAP_BASE_DN}",
                search_filter=search_filter,
                search_scope=SUBTREE,
                attributes=['cn']
            )
            
            if admin_conn.entries:
                # Return the actual DN found
                user_dn = admin_conn.entries[0].entry_dn
                admin_conn.unbind()
                return user_dn
            
            admin_conn.unbind()
            return None
            
        except Exception as e:
            print(f"Error finding user DN for {username}: {e}")
            return None

    @staticmethod
    def get_user_groups(username: str) -> list[str]:
        """Get the groups a user belongs to using admin credentials."""
        server = Server(LDAP_SERVER, port=LDAP_PORT, get_info=ALL)
        
        try:
            # Use admin credentials to search for groups
            admin_conn = Connection(
                server,
                user=LDAP_ADMIN_DN,
                password=LDAP_ADMIN_PASSWORD,
                auto_bind=True
            )
            
            # Find the actual user DN first
            user_dn = LDAPAuth.find_user_dn(username)
            if not user_dn:
                return []
            
            # Search for groups where the user is a member
            search_filter = f"(&(objectClass=groupOfNames)(member={user_dn}))"
            
            admin_conn.search(
                search_base=f"ou=groups,{LDAP_BASE_DN}",
                search_filter=search_filter,
                search_scope=SUBTREE,
                attributes=['cn']
            )
            
            groups = [entry.cn.value for entry in admin_conn.entries]
            admin_conn.unbind()
            return groups
            
        except Exception as e:
            print(f"Error getting groups for {username}: {e}")
            return []

    @staticmethod
    def authenticate_user(username: str, password: str) -> Tuple[bool, Optional[list[str]]]:
        """
        Authenticate user and return their group memberships.
        Returns a tuple of (is_authenticated, groups).
        """
        server = Server(LDAP_SERVER, port=LDAP_PORT, get_info=ALL)
        
        # First find the correct user DN
        user_dn = LDAPAuth.find_user_dn(username)
        if not user_dn:
            print(f"User not found: {username}")
            return False, None
        
        try:
            # Try to bind with the user's credentials
            conn = Connection(
                server,
                user=user_dn,
                password=password,
                auto_bind=True
            )
            
            # If we get here, authentication was successful
            conn.unbind()
            
            # Now get the user's groups using admin credentials
            groups = LDAPAuth.get_user_groups(username)
            
            print(f"Authentication successful for {username} (DN: {user_dn}), groups: {groups}")
            return True, groups
            
        except Exception as e:
            print(f"Authentication failed for {username} (DN: {user_dn}): {e}")
            return False, None

    @staticmethod
    def check_group_access(groups: list[str], required_group: str) -> bool:
        """Check if user has access to the required group."""
        return required_group in groups 