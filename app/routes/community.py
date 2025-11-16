from flask import Blueprint, jsonify, request
from app.db import db
from app.models import CommunityPost, CommunityComment, CommunityLike
from sqlalchemy import desc
import uuid

community_bp = Blueprint('community', __name__, url_prefix='/api/community')

@community_bp.route('/posts', methods=['GET'])
def get_posts():
    """Obtener todos los posts con filtros opcionales"""
    category = request.args.get('category')
    limit = request.args.get('limit', type=int, default=50)
    offset = request.args.get('offset', type=int, default=0)
    
    try:
        query = CommunityPost.query
        
        if category:
            query = query.filter_by(category=category)
        
        posts = query.order_by(desc(CommunityPost.created_at)).limit(limit).offset(offset).all()
        posts_data = [post.to_dict() for post in posts]
        
        return jsonify({
            'success': True,
            'data': posts_data,
            'count': len(posts_data)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@community_bp.route('/posts', methods=['POST'])
def create_post():
    """Crear un nuevo post"""
    try:
        data = request.get_json()
        
        required_fields = ['user_id', 'title', 'content', 'category']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} es requerido'}), 400
        
        post = CommunityPost(
            id=str(uuid.uuid4()),
            user_id=data['user_id'],
            title=data['title'],
            content=data['content'],
            category=data['category']
        )
        
        db.session.add(post)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': post.to_dict(),
            'message': 'Post creado exitosamente'
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@community_bp.route('/posts/<post_id>', methods=['GET'])
def get_post(post_id):
    """Obtener un post específico con sus comentarios"""
    try:
        post = CommunityPost.query.get(post_id)
        
        if not post:
            return jsonify({'error': 'Post no encontrado'}), 404
        
        post_dict = post.to_dict()
        
        # Obtener comentarios
        comments = CommunityComment.query.filter_by(post_id=post_id).order_by(CommunityComment.created_at).all()
        post_dict['comments'] = [comment.to_dict() for comment in comments]
        
        return jsonify({
            'success': True,
            'data': post_dict
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@community_bp.route('/posts/<post_id>', methods=['PUT'])
def update_post(post_id):
    """Actualizar un post"""
    try:
        post = CommunityPost.query.get(post_id)
        
        if not post:
            return jsonify({'error': 'Post no encontrado'}), 404
        
        data = request.get_json()
        
        if 'title' in data:
            post.title = data['title']
        if 'content' in data:
            post.content = data['content']
        if 'category' in data:
            post.category = data['category']
        
        from datetime import datetime
        import pytz
        bolivia_tz = pytz.timezone('America/La_Paz')
        post.updated_at = datetime.now(bolivia_tz)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': post.to_dict(),
            'message': 'Post actualizado exitosamente'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@community_bp.route('/posts/<post_id>', methods=['DELETE'])
def delete_post(post_id):
    """Eliminar un post"""
    try:
        post = CommunityPost.query.get(post_id)
        
        if not post:
            return jsonify({'error': 'Post no encontrado'}), 404
        
        db.session.delete(post)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Post eliminado exitosamente'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@community_bp.route('/posts/<post_id>/comments', methods=['GET'])
def get_post_comments(post_id):
    """Obtener comentarios de un post"""
    try:
        comments = CommunityComment.query.filter_by(post_id=post_id).order_by(CommunityComment.created_at).all()
        comments_data = [comment.to_dict() for comment in comments]
        
        return jsonify({
            'success': True,
            'data': comments_data,
            'count': len(comments_data)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@community_bp.route('/posts/<post_id>/comments', methods=['POST'])
def create_comment(post_id):
    """Crear un comentario en un post"""
    try:
        post = CommunityPost.query.get(post_id)
        
        if not post:
            return jsonify({'error': 'Post no encontrado'}), 404
        
        data = request.get_json()
        
        if 'user_id' not in data or 'content' not in data:
            return jsonify({'error': 'user_id y content son requeridos'}), 400
        
        comment = CommunityComment(
            id=str(uuid.uuid4()),
            post_id=post_id,
            user_id=data['user_id'],
            content=data['content']
        )
        
        db.session.add(comment)
        
        # Actualizar contador de comentarios
        post.comments_count = CommunityComment.query.filter_by(post_id=post_id).count() + 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': comment.to_dict(),
            'message': 'Comentario creado exitosamente'
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@community_bp.route('/posts/<post_id>/like', methods=['POST'])
def toggle_like(post_id):
    """Dar o quitar like a un post"""
    try:
        post = CommunityPost.query.get(post_id)
        
        if not post:
            return jsonify({'error': 'Post no encontrado'}), 404
        
        data = request.get_json()
        
        if 'user_id' not in data:
            return jsonify({'error': 'user_id es requerido'}), 400
        
        user_id = data['user_id']
        
        # Verificar si ya existe el like
        existing_like = CommunityLike.query.filter_by(post_id=post_id, user_id=user_id).first()
        
        if existing_like:
            # Quitar like
            db.session.delete(existing_like)
            post.likes_count = max(0, post.likes_count - 1)
            liked = False
        else:
            # Agregar like
            like = CommunityLike(
                id=str(uuid.uuid4()),
                post_id=post_id,
                user_id=user_id
            )
            db.session.add(like)
            post.likes_count = post.likes_count + 1
            liked = True
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'liked': liked,
            'likes_count': post.likes_count,
            'message': 'Like actualizado exitosamente'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@community_bp.route('/posts/<post_id>/likes', methods=['GET'])
def get_post_likes(post_id):
    """Obtener likes de un post y verificar si un usuario le dio like"""
    try:
        user_id = request.args.get('user_id')
        
        likes = CommunityLike.query.filter_by(post_id=post_id).all()
        likes_count = len(likes)
        
        user_liked = False
        if user_id:
            user_liked = CommunityLike.query.filter_by(post_id=post_id, user_id=user_id).first() is not None
        
        return jsonify({
            'success': True,
            'likes_count': likes_count,
            'user_liked': user_liked
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@community_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        posts_count = CommunityPost.query.count()
        return jsonify({
            'success': True,
            'message': 'Community API is running',
            'posts_count': posts_count
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

