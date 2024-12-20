from flask import Blueprint, jsonify, request
from models import Project, db
from http import HTTPStatus

bp = Blueprint('project', __name__)

@bp.route('', methods=['POST'])
def create_project():
    """
    Create a new project
    ---
    tags:
      - project
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - project_name
          properties:
            project_name:
              type: string
              example: "Authentication Service"
            description:
              type: string
              example: "Keys for authentication service"
    responses:
      201:
        description: Project created successfully
      400:
        description: Invalid request data
    """
    data = request.get_json()
    
    if not data or 'project_name' not in data:
        return jsonify({'error': 'project_name is required'}), HTTPStatus.BAD_REQUEST
    
    project = Project(
        project_name=data['project_name'],
        description=data.get('description', '')
    )
    
    db.session.add(project)
    db.session.commit()
    
    return jsonify({
        'id': project.id,
        'project_name': project.project_name,
        'description': project.description
    }), HTTPStatus.CREATED

@bp.route('', methods=['GET'])
def list_projects():
    """
    List all projects
    ---
    tags:
      - project
    responses:
      200:
        description: List of projects
    """
    projects = Project.query.all()
    return jsonify([{
        'id': p.id,
        'project_name': p.project_name,
        'description': p.description
    } for p in projects]), HTTPStatus.OK

@bp.route('/<int:project_id>', methods=['GET'])
def get_project(project_id):
    """
    Get a specific project
    ---
    tags:
      - project
    parameters:
      - name: project_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Project details
      404:
        description: Project not found
    """
    project = Project.query.get_or_404(project_id)
    return jsonify({
        'id': project.id,
        'project_name': project.project_name,
        'description': project.description
    }), HTTPStatus.OK

@bp.route('/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    """
    Update a project
    ---
    tags:
      - project
    parameters:
      - name: project_id
        in: path
        type: integer
        required: true
      - in: body
        name: body
        schema:
          type: object
          properties:
            project_name:
              type: string
            description:
              type: string
    responses:
      200:
        description: Project updated successfully
      404:
        description: Project not found
    """
    project = Project.query.get_or_404(project_id)
    data = request.get_json()
    
    if 'project_name' in data:
        project.project_name = data['project_name']
    if 'description' in data:
        project.description = data['description']
    
    db.session.commit()
    
    return jsonify({
        'id': project.id,
        'project_name': project.project_name,
        'description': project.description
    }), HTTPStatus.OK

@bp.route('/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    """
    Delete a project
    ---
    tags:
      - project
    parameters:
      - name: project_id
        in: path
        type: integer
        required: true
    responses:
      204:
        description: Project deleted successfully
      404:
        description: Project not found
    """
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    
    return '', HTTPStatus.NO_CONTENT
